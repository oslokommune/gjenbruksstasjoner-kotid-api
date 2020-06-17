# import os
# import json
import boto3
import logging
from typing import List, Optional

# from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from queue_predictions_api.models import Station
from test.mockdata import test_config_data, test_prediction_data

# TODO: Remove mock data

logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3 = boto3.resource("s3", region_name="eu-west-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
# predictions_table = dynamodb.Table(os.environ["REG_PREDICTION_TABLE_NAME"])


class QueuePredictionService:
    def __init__(self):
        self.prediction_config = {}
        self.stations = {}
        self._update_config()

    def get_station(self, station_id) -> Optional[Station]:
        if station_id not in self.stations or not self.stations[station_id].get(
            "active", False
        ):
            return None

        # Update defaults
        station_config = {
            "station_id": station_id,
            "prediction_config": self.prediction_config,
        }
        station_config.update(self.stations[station_id])

        try:
            station = Station.from_dict(station_config)
        except Exception as e:
            logger.exception(e)
            return None

        # Update prediction data
        station.queue_prediction = self._get_prediction_data(station_id)

        return station

    def get_all_stations(self) -> List[Station]:
        return list(
            filter(
                lambda s: s is not None,
                [self.get_station(station_id) for station_id in self.stations.keys()],
            )
        )

    def _get_prediction_data(self, station_id):
        try:
            """
            return predictions_table.query(
                KeyConditionExpression=Key("station_id").eq(station_id),
                ScanIndexForward=False,
                Limit=1,
            )["Items"][0]
            """
            return test_prediction_data.get(station_id)
        except IndexError:
            logger.warning("No prediction data found")
        except ClientError as e:
            logger.exception(e)

    def _update_config(self):
        try:
            """
            obj = s3.Object(
                os.environ["REG_CONFIG_BUCKET"], os.environ["REG_CONFIG_IDENTIFIER"]
            )
            config = json.loads(obj.get()["Body"].read())
            """
            config = test_config_data
        except Exception as e:
            logging.exception(e)
            return
        else:
            self.prediction_config = config.get("prediction_config", {})
            self.stations = config.get("stations", {})
