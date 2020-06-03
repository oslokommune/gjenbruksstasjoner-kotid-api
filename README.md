Gjenbruksstasjoner Queue Time API
=========================

Lambda function providing an API for [Gjenbruksstasjoner Queue Time Predictions](https://github.oslo.kommune.no/origo-dataplatform/gjenbruksstasjoner-queue-predictions) usings [Flask](https://flask.palletsprojects.com/) and [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/).


## Tests

Tests are run using [tox](https://pypi.org/project/tox/): `make test`

For tests and linting we use [pytest](https://pypi.org/project/pytest/),
[flake8](https://pypi.org/project/flake8/) and
[black](https://pypi.org/project/black/).


## Run

`make run` to start up Flask app locally.


## Deploy

`make deploy` or `make deploy-prod`

Requires `saml2aws`
