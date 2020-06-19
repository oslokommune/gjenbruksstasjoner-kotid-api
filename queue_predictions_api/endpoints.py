import logging
from flask_restful import Resource, marshal_with, abort, fields

from queue_predictions_api.service import QueuePredictionService


logger = logging.getLogger("queue_predictions_api.endpoints")


class RoundedFloat(fields.Float):
    def format(self, value):
        return round(value, 3)


station_fields = {
    "station_id": fields.Integer,
    "station_name": fields.String(attribute="pretty_name"),
    "is_open": fields.Boolean,
    "queue": fields.Nested(
        {
            "is_full": fields.Boolean,
            "expected_time": RoundedFloat(attribute="expected_queue_time"),
            "min_time": RoundedFloat(attribute="min_queue_time"),
            "max_time": RoundedFloat(attribute="max_queue_time"),
            "updated_at": fields.DateTime("iso8601"),
        },
        allow_null=True,
        attribute="queue_prediction",
    ),
}


class StationListResource(Resource):
    @marshal_with(station_fields)
    def get(self):
        queue_prediction_service = QueuePredictionService()
        return queue_prediction_service.get_all_stations()


class StationResource(Resource):
    @marshal_with(station_fields)
    def get(self, station_id):
        queue_prediction_service = QueuePredictionService()
        station = queue_prediction_service.get_station(station_id)

        if not station:
            abort(404, message="No station data found for provided id")

        return station
