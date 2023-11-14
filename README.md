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

* `dupla.payload.KtrPayload`
* `dupla.payload.LigPayload`
* `dupla.payload.MomsPayload`
* `dupla.payload.KtrObsPayload`
* `dupla.payload.LonsumPayload`
* `dupla.payload.SelskabSambeskatningPayload`
* `dupla.payload.SelskabSelvangivelsePayload`

Please c.f. the docs of the respective classes for more information
on what each endpoint is for. Each payload model is a Pydantic model, so inputs
are validated.


### Using the base API

The base api access class can be used as following.
In this example, we access the VAT (Moms in Danish) endpoint.

```python
from datetime import date, timedelta
from uuid import uuid4
import dupla
from dupla import DuplaApiKeys

api = dupla.DuplaAccess(
    transaction_id=str(uuid4()),
    agreement_id="your-aftale-id-goes-here",
    pkcs12_filename="path-to-cert-file",
    pkcs12_password="goodpassword",
    billetautomat_url="https://oces.billetautomat.skat.dk/auth/realms/oces/certificates/cert",
    jwt_token_expiration_overlap=5
)

# lets see if this company (se_number 98765432) has done any VAT the last year
kwargs = {DuplaApiKeys.SE: ["98765432"],
          DuplaApiKeys.AFREGNING_START: date.today() - timedelta(days=365),
          DuplaApiKeys.AFREGNING_SLUT: date.today()}
payload = dupla.payload.MomsPayload(**kwargs)

data = api.get_data(payload)

print(data)
```

© ERST 2023
