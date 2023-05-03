from typing import Dict, Type
import os
import yaml
import uuid
from datetime import datetime, timedelta
from urllib.parse import urljoin

import dotenv

import dupla as dp

# Define a dictionary mapping the name of the entry in the aftaler.yml
# to the API endpoint class.
ENDPOINTS: Dict[str, Type[dp.DuplaEndpointApiBase]] = {
    "moms": dp.DuplaMomsApi,
    "ligning": dp.DuplaLigApi,
    "kontrol": dp.DuplaKtrApi,
    "kontrolobs": dp.DuplaKtrObsApi,
    "lønsum": dp.DuplaLonsumApi,
    "selskab_sambeskatning": dp.DuplaSelskabSambeskatningApi,
    "selskab_selvangivelse": dp.DuplaSelskabSelvangivelseApi,
}

skips = ["lønsum"]

# Load the agreements and environment variables.
dotenv.load_dotenv("./.env")
AGREEMENTS_FILE = "./agreements.yml"


def get_agreements():
    with open(AGREEMENTS_FILE, "r") as file:
        return yaml.safe_load(file)


def get_agreement(name: str):
    try:
        return get_agreements()[name]
    except KeyError:
        raise ValueError(f"No agreement with name: '{name}'") from None


def make_api(name: str):
    agreement = get_agreement(name)
    factory = ENDPOINTS[name]

    env = os.environ  # Alias
    endpoint = agreement.get("endpoint", factory.DEFAULT_ENDPOINT)
    endpoint_url = urljoin(env["DUPLA_API_URL"], endpoint)
    print("URL", endpoint_url)

    api = factory(
        endpoint=endpoint_url,
        transaction_id=str(uuid.uuid4()),
        agreement_id=agreement["id"],
        pkcs12_filename=env["DUPLA_CERT_FILE"],
        pkcs12_password=env["DUPLA_PASSWORD"],
        billetautomat_url=env["BILLETAUTOMAT_URL"],
        jwt_token_expiration_overlap=5,
        max_tries=1,
    )
    return api


def make_payload_args(api_name: str):
    api = ENDPOINTS[api_name]
    k = dp.DuplaApiKeys  # Alias
    to_date = datetime.now()
    from_date = to_date - timedelta(days=2 * 365)
    # Dummy datas
    data = {
        k.CVR: ["12345678", 12345678],
        k.SE: ["98765432"],
        k.CPR: ["0000000000"],
        k.AFREGNING_START: from_date,
        k.AFREGNING_SLUT: to_date,
        k.UDSTILLING_FRA: from_date,
        k.UDSTILLING_TIL: to_date,
        k.TEKNISK_REGISTRERING_FRA: from_date,
        k.TEKNISK_REGISTRERING_TIL: to_date,
    }
    payload = {key: data[key] for key in api.FIELDS if key in data}

    if api_name == "ligning":
        # Technically allowed, but not with our current agreement
        payload.pop(k.SE)

    return payload


def run_endpoint(name: str) -> None:
    api = make_api(name)
    kwargs = make_payload_args(name)

    payload = api.get_payload(**kwargs)
    api.get_data(payload)


if __name__ == "__main__":
    all_agreements = get_agreements()

    for endp in all_agreements:
        print("Running", endp)
        try:
            run_endpoint(endp)
            print("Ok!")
        except Exception as e:
            print("Error!", e)
