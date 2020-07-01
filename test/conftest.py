import os
import json
import boto3
import pytest
import decimal
from moto import mock_dynamodb2, mock_s3

from test.mockdata import test_config_data, test_prediction_data
from app import app as flask_app


aws_region = "eu-west-1"
table_name = os.environ["REG_PREDICTION_TABLE_NAME"]
bucket_name = os.environ["REG_CONFIG_BUCKET"]
config_identifier = os.environ["REG_CONFIG_IDENTIFIER"]


def create_predictions_table(items=[]):
    client = boto3.client("dynamodb", region_name=aws_region)
    client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "station_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "station_id", "AttributeType": "N"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        GlobalSecondaryIndexes=[],
    )

    table = boto3.resource("dynamodb", region_name=aws_region).Table(table_name)

    for item in items:
        table.put_item(Item=json.loads(json.dumps(item), parse_float=decimal.Decimal))

    return table


def create_config_file(config):
    s3 = boto3.resource("s3", region_name=aws_region)
    s3object = s3.Object(bucket_name, config_identifier)

    s3object.put(Body=json.dumps(config).encode())

    return s3object


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


@pytest.fixture(scope="function")
def mock_s3_config():
    mock_s3().start()

    client = boto3.client("s3", region_name=aws_region)
    client.create_bucket(Bucket=bucket_name)


@pytest.fixture(scope="function")
def config_data():
    return test_config_data


@pytest.fixture(scope="function")
def prediction_data():
    return test_prediction_data
