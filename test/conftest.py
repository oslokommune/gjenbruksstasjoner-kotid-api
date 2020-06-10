import boto3
import pytest

# import datetime
from moto import mock_dynamodb2

from app import app as flask_app
from queue_predictions_api.data import predictions_table_name as table_name


def create_predictions_table(items=[], region="eu-west-1"):
    client = boto3.client("dynamodb", region_name=region)
    client.create_table(
        # TODO
    )

    table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    for item in items:
        table.put_item(Item=item)

    return table


@pytest.fixture
def mock_client():
    # Configure the application for testing and disable error catching during
    # request handling for better reports. Required in order for exceptions
    # to propagate to the test client.
    # https://flask.palletsprojects.com/en/1.1.x/testing/
    # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.test_client
    flask_app.config["TESTING"] = True

    with flask_app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def mock_dynamodb():
    mock_dynamodb2().start()
