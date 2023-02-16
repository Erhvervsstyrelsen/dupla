# Project description
A Python API for [DUPLA](https://dataudveksling.skat.dk/) (Dataudvekslingsplatformen)

A list of the services available can be found [here](https://dataudveksling.skat.dk/#/servicekatalog)

## SETUP

For development
`python -m venv .venv`

`source .venv/bin/activate`

`pip install -r dev-requirements.txt`

Run tests:
`pytest tests/`

## GETTING STARTED

```
from uuid import uuid4
from datetime import date, timedelta

from dupla import DuplaApiBase

api = DuplaApiBase(
    transaktions_id=str(uuid4()),
    aftale_id="your-aftale-id-goes-here",
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