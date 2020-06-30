import os
import json
import boto3
import logging
from typing import List, Optional

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from queue_predictions_api.models import Station, PredictionConfig


logger = logging.getLogger("queue_predictions_api.service")


s3 = boto3.resource("s3", region_name="eu-west-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
predictions_table = dynamodb.Table(os.environ["REG_PREDICTION_TABLE_NAME"])


class QueuePredictionService:
    def __init__(self):
        self.prediction_config = {}
        self.stations = {}
        self._update_config()

    def get_station(self, station_id: int) -> Optional[Station]:
        station_config = self.stations.get(str(station_id))

        if not station_config:
            return None

        try:
            prediction_config = self.prediction_config.copy()

            if station_config.get("prediction_config"):
                # Update defaults with station specific config
                prediction_config.update(station_config["prediction_config"])

            station = Station(
                station_id=station_id,
                prediction_config=PredictionConfig.from_dict(prediction_config),
                station_name=station_config.get("station_name"),
                opening_hours=station_config.get("opening_hours"),
            )
        except Exception as e:
            logger.error("Could not create station object from provided configuration")
            logger.exception(e)
            return None

        # Update prediction data
        if station.prediction_config.prediction_enabled and station.is_open:
            station.queue_prediction = self._get_prediction_data(station.station_id)

        return station

    def get_all_stations(self) -> List[Station]:
        return list(
            filter(
                lambda s: s is not None,
                [
                    self.get_station(int(station_id))
                    for station_id in self.stations.keys()
                ],
            )
        )

    def _get_prediction_data(self, station_id: int) -> Optional[dict]:
        try:
            return predictions_table.query(
                KeyConditionExpression=Key("station_id").eq(station_id),
                ScanIndexForward=False,
                Limit=1,
            )["Items"][0]
        except IndexError:
            logger.warning(f"No prediction data found for station {station_id}")
        except ClientError as e:
            logger.error(
                f"Could not get queue prediction data for station {station_id}"
            )
            logger.exception(e)

    def _update_config(self):
        logger.info("Reading remote configuration data")

        try:
            obj = s3.Object(
                os.environ["REG_CONFIG_BUCKET"], os.environ["REG_CONFIG_IDENTIFIER"]
            )
            config = json.loads(obj.get()["Body"].read())
        except Exception as e:
            logger.error("Could not read remote configuration file")
            logger.exception(e)
            return
        else:
            self.prediction_config = config.get("prediction_config", {})
            self.stations = config.get("stations", {})

            if not self.prediction_config:
                logger.warning("No global prediction configuration found")
            if not self.stations:
                logger.warning("No stations found in configuration")
