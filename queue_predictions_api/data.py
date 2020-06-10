# import json
import boto3
import logging
import datetime

# from boto3.dynamodb.conditions import Key
# from botocore.exceptions import ClientError


TEST_CONFIG = {
    "margin_of_error": 0.25,
    "queue_full_certainty_threshold": 0.9,
    "queue_not_full_certainty_threshold": 0.5,
    "Haraldrud": {"active": True},
}
TEST_DB_DATA = [
    {
        "station_id": 41,
        "queue_full": 0.04,
        "expected_queue_time": 0.333,
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
s3 = boto3.resource("s3", region_name="eu-west-1")

# dynamodb = session.resource("dynamodb", region_name="eu-west-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
predictions_table_name = "gjenbruksstasjoner-estimert-kotid"
predictions_table = dynamodb.Table(predictions_table_name)


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


def download_config():
    return TEST_CONFIG
    """
    try:
        obj = s3.Object(
            "ok-origo-dataplatform-dev", "test/petter-testing-bucket/reg_config.json"
        )
        return json.loads(obj.get()["Body"].read())
    except ClientError as e:
        logging.exception(e)
    """
