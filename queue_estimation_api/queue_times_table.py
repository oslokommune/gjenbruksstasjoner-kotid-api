import boto3
import logging
import datetime

# from boto3.dynamodb.conditions import Key
# from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# session = boto3.Session(profile_name="saml-origo-dev")
# dynamodb = session.resource("dynamodb", region_name="eu-west-1")

dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
queue_times_table = dynamodb.Table("gjenbruksstasjoner-estimert-kotid")


db_queue_data = {
    "key": "test/espeng-testing-bucket/prediction_testing/pre-processed_images/station_id_41_20200506T103000.bin",
    "queue_end_pos": 959.6093139648438,
    "queue_lanes": 1.3786303497909103e-05,
    "queue_full": 4.971436283085495e-06,
    "cars": 14.125636782941122,
    "expected_queue_time": 0.17657045978676403,
    "updated_at": datetime.datetime.now()
    # "updated_at": "asdasd"
}


def get_all_estimations():
    """
    try:
        estimations = queue_times_table.scan()["Items"]
    except ClientError as e:
        logger.exception(e)
        return []
    return estimations
    """
    return [db_queue_data, db_queue_data, db_queue_data]


def get_estimation_by_station(station_id):
    """
    try:
        estimations = queue_times_table.query(
            KeyConditionExpression=Key("dataset_id").eq(station_id)
            & Key("date").eq("2020-04-14")
        )["Items"]
    except ClientError as e:
        logger.exception(e)
        return None
    return next(iter(estimations), None)
    """
    return db_queue_data
