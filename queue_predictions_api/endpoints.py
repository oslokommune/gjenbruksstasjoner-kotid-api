import logging
from flask_restful import Resource, marshal_with, abort, fields

from queue_predictions_api.models import Config


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RoundedFloat(fields.Float):
    def format(self, value):
        return round(value, 3)


class NestedField(fields.Nested):
    def output(self, key, obj):
        """ Do not return empty nested fields. """
        if not obj or getattr(obj, key) is None:
            return None
        return super().output(key, obj)


station_fields = {
    "station_id": fields.Integer,
    "station_name": fields.String(attribute="pretty_name"),
    "is_open": fields.Boolean,
    "queue": NestedField(
        {
            "is_full": fields.Boolean,
            "expected_time": RoundedFloat(attribute="expected_queue_time"),
            "min_time": RoundedFloat(attribute="min_queue_time"),
            "max_time": RoundedFloat(attribute="max_queue_time"),
            "updated_at": fields.DateTime("iso8601"),
        }
    ),
}


class StationResource(Resource):
    @marshal_with(station_fields)
    def get(self, station_id):
        try:
            config = Config()
        except Exception as e:
            logger.exception(e)
            abort(500)

        station = config.get_station(station_id)

        if not station:
            abort(404)

        return station
