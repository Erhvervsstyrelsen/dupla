# Project description
A Python API for [DUPLA](https://dataudveksling.skat.dk/) (Dataudvekslingsplatformen)

A list of the services available can be found [here](https://dataudveksling.skat.dk/#/servicekatalog)

## Setup

For development
`python -m venv .venv`

`source .venv/bin/activate`

`pip install ".[test]"`

Run tests:
`pytest tests/`

## Getting Started

### Using pre-defined API endpoints

This package defines some endpoints which has some (limited) knowledge
of the API schema used by SKAT. The classes are:

* `dupla.DuplaKtrApi`
* `dupla.DuplaLigApi`
* `dupla.DuplaMomsApi`
* `dupla.DuplaKtrObsApi`
* `dupla.DuplaLonsumApi`
* `dupla.DuplaSelskabSambeskatningApi`
* `dupla.DuplaSelskabSelvangivelseApi`

Please c.f. the docs of the respective classes for more information
on what each endpoint is for. An example using the VAT (Moms in Danish) endpoint:

```python
from uuid import uuid4
from datetime import date
from dupla import DuplaMomsApi, DuplaApiKeys

# Get the default VAT endpoint from the skat api
endpoint = DuplaMomsApi.endpoint_from_base_url("https://api.skat.dk")

api = DuplaMomsApi(
    endpoint=endpoint,
    transaction_id=str(uuid4()),
    agreement_id="your-aftale-id-goes-here",
    pkcs12_filename="path-to-cert-file",
    pkcs12_password="goodpassword",
    billetautomat_url="https://oces.billetautomat.skat.dk/auth/realms/oces/certificates/cert",
    jwt_token_expiration_overlap=5
)

# datetime objects are automatically converted
# into the correct string representation
payload = {
    DuplaApiKeys.SE=["98765432"],
    DuplaApiKeys.UDSTILLING_FRA=date.today() - timedelta(days=365),
    DuplaApiKeys.UDSTILLING_TIL=date.today()
}
data = api.get_data(payload, format_payload=True, validate_payload=True)

print(data)
```

The fields which can be provided is given by the `api.FIELDS` dictionary,
which is a key-value set of the API key as well as whether the key is required
by the SKAT api. Should a key you wish to provide be missing, a consistency check of
unknown keys can be disabled by setting `api.allow_unknown_fields = True`.

#### Testing your API
A description of how to test your API can be found [here](./scripts/README.md).

### Using the base API

The base api can be used as following:

```python
from uuid import uuid4
from datetime import date, timedelta

from dupla.base import DuplaApiBase

api = DuplaApiBase(
    transaction_id=str(uuid4()),
    agreement_id="your-aftale-id-goes-here",
    pkcs12_filename="path-to-cert-file",
    pkcs12_password="goodpassword",
    billetautomat_url="https://oces.billetautomat.skat.dk/auth/realms/oces/certificates/cert",
    jwt_token_expiration_overlap=5
)

# lets see if this company (se_number 9876543210) has done any VAT the last year
payload = {
    "VirksomhedSENummer": "9876543210",
    "AfregningPeriodeForholdPeriodeStartDato": "2010-12-31",
    "AfregningPeriodeForholdPeriodeSlutDato": date.today().isoformat(),
    "UdstillingRegistreringFra": (date.today() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "UdstillingRegistreringTil": date.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
}

response = api.get(
    url="https://api.skat.dk/Momsangivelse",
    params=payload
)

# prints the whole response, use response.json().get("data") for data only
print(response.json())
```

© ERST 2023
