# Testing the DUPLA endpoints

The [run_endpoints.py](./run_endpoints.py) file provides a test
framework, where you can test the DUPLA API endpoints with your
own configurations.

To get started, make a local copy of the
[agreements.yml.dist](./agreements.yml.dist) and
[env.dist](./env.dist) files:

```bash
cp agreements.yml.dist agreements.yml
cp env.dist .env
```

The `run_endpoints.py` script should target the files you just created.
So if you use different names, ensure you change the `run_endpoints.py`
script accordingly.

Next, fill out the necessary details in the newly created
`.env` and `agreements.yml` files. Below is a description of the variables
in the `.env` file:

| Variable          | Description                                                                                                                                                                                 |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DUPLA_API_URL     | The base URL to the SKAT API, such as `https://api.skat.dk` or `https://api.tfe.skat.dk`.                                                                                                   |
| DUPLA_CERT_FILE   | Location to the certificate file for the "billetautomat", e.g. `~/certs/my_dupla_certificate.p12`.                                                                                          |
| DUPLA_PASSWORD    | The password to the certificate file.                                                                                                                                                       |
| BILLETAUTOMAT_URL | The URL to the "billetautomat", e.g. `https://oces.billetautomat.skat.dk/auth/realms/oces/certificates/cert` or `https://oces.billetautomat-uat.skat.dk/auth/realms/oces/certificates/cert` |

The `agreements.yml` file is a collection of the active agreements
you wish to check. The `Id` field should be populated with the
UUID of your agreement with SKAT for the corresponding service.
The API class which is going to run your agreement is specified in
the `ENDPOINTS` dictionary in the `run_scripts.py` file. The keys
of the `ENDPOINTS` dictionary should correspond to the agreement
names specified in the `agreements.yml` file, e.g. if you
have an agreement for the "Momsangivelse", the default name in
the `run_scripts.py` mapping is `moms`.

Once you have specified all of the environment variables, run the
`run_endpoints.py` script. It will populate the API calls
with dummy data. If you wish to test some specific data,
you can modify the `make_payload_args` function accordingly.

*Note*: Be careful not commit your personal secrets to the git repo.
The default filenames will be ignored in the `.gitignore` file,
but if you use a different name keep that in mind.
