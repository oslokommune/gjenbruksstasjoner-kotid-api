import logging
from flask_restful import Resource, marshal_with, abort, fields

import queue_predictions_api.data as data
from queue_predictions_api.models import PredictionConfig, StationQueue


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RoundedFloat(fields.Float):
    def format(self, value):
        return round(value, 3)


class NestedQueuePrediction(fields.Nested):
    def output(self, key, station):
        if station.is_open and station.is_queue_full is not None:
            return super().output(key, station)


prediction_fields = {
    "is_full": fields.Boolean,
    "expected_time": RoundedFloat,
    "min_time": RoundedFloat,
    "max_time": RoundedFloat,
}
station_fields = {
    "station_id": fields.Integer,
    "station_name": fields.String,
    "is_open": fields.Boolean,
    "queue": NestedQueuePrediction(prediction_fields, attribute="queue_prediction"),
}


class Station(Resource):
    @marshal_with(station_fields)
    def get(self, station_id):
        try:
            # TODO: Download for each request? Defaults?
            config = PredictionConfig(**data.download_config())
        except Exception as e:
            logger.exception(e)
            abort(500, message="config error")

        prediction_data = data.get_prediction_by_station_id(station_id)

        if not prediction_data:
            abort(404, message="No queue prediction found for station")

        try:
            station_queue = StationQueue(config, **prediction_data)
        except Exception as e:
            logger.exception(e)
            abort(500, message="hei")

        return station_queue
