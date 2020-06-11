# import os
# import json
# import boto3
import logging
import datetime

# from boto3.dynamodb.conditions import Key
# from botocore.exceptions import ClientError


TEST_CONFIG = {
    "prediction_config": {
        "margin_of_error": 0.25,
        "queue_full_certainty_threshold": 0.9,
        "queue_not_full_certainty_threshold": 0.5,
    },
    "stations": {
        41: {
            "active": True,
            "pretty_name": "Grønmo",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
            },
        },
        42: {
            "active": True,
            "pretty_name": "Haraldrud gjenbruksstasjon",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
                "deviations": {
                    "2020-12-24": None,
                    # "2020-06-11": {"open": "08:00", "closed": "12:04"},
                },
            },
            "prediction_config": {
                "margin_of_error": 0.3,
                "queue_full_certainty_threshold": 0.9,
                "queue_not_full_certainty_threshold": 0.5,
            },
        },
    },
}
TEST_DB_DATA = [
    {
        "station_id": 41,
        "queue_full": 0.1,
        "expected_queue_time": 0.5,
        "updated_at": datetime.datetime.now(),
    },
    {
        "station_id": 42,
        "queue_full": 0.04,
        "expected_queue_time": 0.333,
        "updated_at": datetime.datetime.now(),
    },
]


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# session = boto3.Session(profile_name="saml-origo-dev")

# s3 = session.resource("s3", region_name="eu-west-1")
# s3 = boto3.resource("s3", region_name="eu-west-1")

# dynamodb = session.resource("dynamodb", region_name="eu-west-1")
# dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
# predictions_table = dynamodb.Table(os.environ["REG_PREDICTION_TABLE_NAME"])


def get_prediction_by_station_id(station_id):
    return TEST_DB_DATA[0]
    """
    try:
        return predictions_table.query(
            KeyConditionExpression=Key("dataset_id").eq(station_id)
            & Key("date").eq("2020-04-14")
        )["Items"][0]
    except ClientError as e:
        logger.exception(e)
    """


def get_config():
    return TEST_CONFIG
    """
    try:
        obj = s3.Object(
            os.environ["REG_CONFIG_BUCKET"], os.environ["REG_CONFIG_IDENTIFIER"]
        )
        return json.loads(obj.get()["Body"].read())
    except ClientError as e:
        logging.exception(e)
    """
