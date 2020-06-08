import logging
from flask_restful import fields


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class StationIdField(fields.String):
    def format(self, value):
        # TODO: Format value (?)
        return value.split("/")[-1]


class QueueFullField(fields.Float):
    def format(self, value):
        try:
            # TODO: Format value
            return 0.12
        except Exception as e:
            logger.exception(e)


class QueueTimeInMinutesField(fields.Float):
    def format(self, value):
        try:
            return round((float(value) * 60), 1)
        except Exception as e:
            logger.exception(e)


class UpdatedAtField(fields.DateTime):
    def format(self, value):
        return value.isoformat()


queue_item_fields = {
    "station_id": StationIdField(attribute="key"),
    "queue_full": QueueFullField(),
    "estimated_queue_time": QueueTimeInMinutesField(
        # default=None
        attribute="expected_queue_time"
    ),
    "updated_at": UpdatedAtField(),
}
