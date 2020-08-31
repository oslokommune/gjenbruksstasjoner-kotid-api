import os
import json
import boto3
import pytest
import decimal
from moto import mock_dynamodb2, mock_s3

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
    return {
        "prediction_config": {
            "prediction_enabled": True,
            "margin_of_error": 0.25,
            "queue_full_certainty_threshold": 0.9,
            "queue_not_full_certainty_threshold": 0.5,
            "outdated_after_minutes": 15,
        },
        "stations": {
            31: {
                "station_name": "Haraldrud hageavfallsmottak",
                "opening_hours": {
                    "default": {"open": "07:00", "closed": "21:00"},
                    "saturday": {"open": "07:00", "closed": "17:00"},
                    "sunday": None,
                },
            },
            41: {
                "station_name": "Grønmo",
                "opening_hours": {
                    "default": {"open": "07:00", "closed": "21:00"},
                    "saturday": {"open": "07:00", "closed": "17:00"},
                    "sunday": None,
                },
            },
            42: {
                "station_name": "Haraldrud gjenbruksstasjon",
                "opening_hours": {
                    "default": {"open": "07:00", "closed": "21:00"},
                    "saturday": {"open": "07:00", "closed": "17:00"},
                    "sunday": None,
                    "deviations": {
                        "2020-12-24": None,
                        "2020-06-11": {"open": "08:00", "closed": "16:00"},
                        "2020-06-17": {"open": "08:00", "closed": "12:00"},
                    },
                },
                "prediction_config": {
                    "prediction_enabled": True,
                    "margin_of_error": 0.3,
                    "queue_full_certainty_threshold": 0.9,
                    "queue_not_full_certainty_threshold": 0.5,
                    "outdated_after_minutes": 20,
                },
                "show_station": True,
            },
            43: {
                "station_name": "Smestad",
                "opening_hours": {},
                "prediction_config": {"prediction_enabled": False},
                "show_station": False,
            },
            44: {
                "station_name": "Heggvin",
                "opening_hours": {},
                "prediction_config": {},
            },
            45: {},
        },
    }


@pytest.fixture(scope="function")
def prediction_data():
    return {
        41: {
            "station_id": 41,
            "queue_full": 0.1,
            "expected_queue_time": 0.5,
            "timestamp": 1591009200.0,  # 2020-06-01 11:00:00
        },
        42: {
            "station_id": 42,
            "queue_full": 0.74,  # UNCERTAIN
            "expected_queue_time": 0.712,
            "timestamp": 1591012800.0,  # 2020-06-01 12:00:00
        },
        31: {
            "station_id": 31,
            "queue_full": 0.1,
            "expected_queue_time": 0.5,
            "timestamp": 1591005600.0,  # 2020-06-01 10:00:00 (OUTDATED)
        },
    }
