gjenbruksstasjoner-kotid-api
=========================

Lambda function providing an API for [gjenbruksstasjoner-kotid-estimering](https://github.oslo.kommune.no/origo-dataplatform/gjenbruksstasjoner-kotid-estimering) using [Flask](https://flask.palletsprojects.com/) and [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/).


## Tests

Tests are run using [tox](https://pypi.org/project/tox/): `make test`

For tests and linting we use [pytest](https://pypi.org/project/pytest/),
[flake8](https://pypi.org/project/flake8/) and
[black](https://pypi.org/project/black/).


## Run

`make run` to start up Flask app locally. Binds to port `5000` by default. Change port/environment:

```
export FLASK_ENV=development
export FLASK_RUN_PORT=8080
```


## Deploy

Deploy to dev is automatic via GitHub Actions, while deploy to prod can be triggered with GitHub Actions via dispatch. You can alternatively deploy from local machine (requires `saml2aws`) with: `make deploy` or `make deploy-prod`.
