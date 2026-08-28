import asyncio
import logging
from typing import Any, AsyncIterator, Dict, Iterable, List, NamedTuple, Optional

import backoff
import httpx

from dupla.retry import parse_header_retry_after, stop_retry_on_err

from .async_base import AsyncDuplaApiBase
from .exceptions import DuplaApiUsageException, DuplaResponseException
from .payload import BasePayload

logger = logging.getLogger(__file__)

__all__ = ["AsyncDuplaAccess", "EntityResult"]

RESPONSE_T = Dict[str, Any]


class EntityResult(NamedTuple):
    """The outcome of querying a single entity via `AsyncDuplaAccess.results`."""

    entity: BasePayload
    data: Optional[List[RESPONSE_T]] = None
    error: Optional[Exception] = None

    @property
    def success(self) -> bool:
        return self.error is None


class AsyncDuplaAccess(AsyncDuplaApiBase):
    """Async client for querying many entities against the Dataudveklspingsplatformen API
    (Dupla) concurrently.

    Usage:
        async with AsyncDuplaAccess(..., max_concurrency=10) as client:
            client.entities = payloads
            async for result in client.results:
                if result.success:
                    ...
                else:
                    ...

    `entities` may be assigned a new iterable to run another batch through the same client.
    `results` is built and cached on first access - iterating it a second time yields no
    further items, since the underlying stream has already run to completion.
    """

    def __init__(
        self,
        transaction_id: str,
        agreement_id: str,
        pkcs12_filename: str,
        pkcs12_password: str,
        billetautomat_url: str,
        base_url: str = r"https://api.skat.dk",
        jwt_token_expiration_overlap: int = 5,
        max_tries: int = 8,
        timeout: float = 30.0,
        max_concurrency: int = 10,
    ):
        """Instantiates new async DUPLA API endpoint client.
        Args:
            base_url (str): The HTTP(S) endpoint of the API.
            transaction_id (str): An ID used to correlate requests across the API.
                Should be constant for IKP-DA.
            agreement_id (str): An ID/token supplied by the API provider.
            pkcs12_filename (str): Path to PKCS12 certificate file.
            pkcs12_password (str): Password for PKCS12 certificate file.
            billetautomat_url (str): Endpoint to the authentication service for requesting
                JWT tokens.
            jwt_token_expiration_overlap (int): The overlap time for token expiration time
                (in seconds) to avoid situations where token is almost expired during the check
                and will be rejected in a next request. Defaults to 5 seconds.
            max_tries (int): Maximum number of times a failed request is re-attempted per
                entity. Defaults to 8.
            timeout (float): Timeout [s] for HTTP requests. Default: 30s.
                Please note:
                  - Timeout is packet-to-packet timeout. See
                    https://www.python-httpx.org/advanced/timeouts/ .
                  - Timeout affects the inner loop of retries. So more retries (`max_retries`)
                    the longer total timeout effect.
            max_concurrency (int): Maximum number of entities queried concurrently.
                Defaults to 10.
        """
        self.base_url = base_url
        self.max_tries = max_tries
        self.max_concurrency = max_concurrency
        self._entities: Optional[Iterable[BasePayload]] = None
        self._results: Optional[AsyncIterator[EntityResult]] = None
        super().__init__(
            transaction_id,
            agreement_id,
            pkcs12_filename,
            pkcs12_password,
            billetautomat_url,
            jwt_token_expiration_overlap,
            timeout,
        )

    @property
    def entities(self) -> Optional[Iterable[BasePayload]]:
        return self._entities

    @entities.setter
    def entities(self, value: Iterable[BasePayload]) -> None:
        self._entities = value
        # Reset the cached stream, so a freshly assigned batch is actually queried.
        self._results = None

    @property
    def results(self) -> AsyncIterator[EntityResult]:
        """An async-iterable of `EntityResult`, one per entity in `.entities`, yielded as
        each entity's query completes. Built and cached on first access."""
        if self._entities is None:
            raise DuplaApiUsageException(
                "No entities have been set. Assign `.entities` before reading `.results`."
            )
        if self._results is None:
            self._results = self._stream(self._entities)
        return self._results

    async def _stream(self, entities: Iterable[BasePayload]) -> AsyncIterator[EntityResult]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _bound(entity: BasePayload) -> EntityResult:
            async with semaphore:
                try:
                    data = await self.get_data(entity)
                    return EntityResult(entity=entity, data=data)
                except Exception as e:
                    return EntityResult(entity=entity, error=e)

        tasks = [asyncio.ensure_future(_bound(entity)) for entity in entities]
        for task in asyncio.as_completed(tasks):
            yield await task

    def get_endpoint(self, payload: BasePayload) -> str:
        """Retrieve the endpoint URL."""
        return payload.__class__.endpoint_from_base_url(self.base_url)

    async def get_data(
        self,
        payload: BasePayload,
        endpoint: Optional[str] = None,
    ) -> List[RESPONSE_T]:
        """Request the server for data.

        Args:
            payload (BasePayload): The Pydantic payload model.
            endpoint (Optional[str], optional): An optional endpoint URL override.
                If not provided, it defaults to the url join of the base URL and
                the payload default URL. Defaults to None.
        Returns:
            List[Dict[str, Any]]: A JSON list representing data as returned by the API.
        """
        if endpoint is None:
            endpoint = self.get_endpoint(payload)
        payload_serialized = payload.get_payload()
        return await self._run_payload(payload_serialized, endpoint)

    async def _run_payload(self, payload: Dict[str, Any], endpoint: str) -> List[RESPONSE_T]:
        """Execute a given payload. No conversion is done on the payload."""

        # Construct the getter with a backoff, and a modified number of max tries
        @backoff.on_exception(
            backoff.expo,
            (httpx.HTTPError),
            giveup=lambda e: stop_retry_on_err(e),
            max_tries=self.max_tries,
        )
        @backoff.on_predicate(
            backoff.runtime,
            predicate=lambda r: r in (429, 503),
            value=lambda r: parse_header_retry_after(r.headers),
            max_tries=self.max_tries,
            jitter=None,
        )
        async def _getter():
            response = await self.get(endpoint, params=payload)
            response.raise_for_status()

            try:
                response_json: Dict[str, Any] = response.json()

                # Perform simple type check to fail fast if the server has returned
                # something unknown.
                data = response_json["data"]
                if not isinstance(data, list):
                    logger.exception(
                        "Received an invalid response from DUPLA, which was not a list: %s", data
                    )
                    raise DuplaResponseException(
                        "Invalid response from DUPLA. The data key did not contain a list.",
                        response=response,
                    )
                return data
            except DuplaResponseException as e:
                # Let the inner exception through
                raise e
            except Exception as e:
                logger.exception("Error occurred while processing response: %s", response.content)
                raise DuplaResponseException(
                    "An error occurred while parsing the DUPLA response.",
                    response=response,
                ) from e

        return await _getter()
