import logging
from flask_restful import Resource, marshal_with, abort

import queue_estimation_api.queue_times_table as queue_times_table
import queue_estimation_api.queue_model as model

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Queues(Resource):
    @marshal_with(model.queue_item_fields)
    def get(self, station_id=None):
        if station_id:
            logger.info(f"Getting estimated queue time for station {station_id}")

            estimation = queue_times_table.get_estimation_by_station(station_id)

            if not estimation:
                abort(
                    404,
                    message=f"No queue time estimation found for {station_id}",
                )

            return estimation

        logger.info("Returning estimated queue time for all stations")

        return queue_times_table.get_all_estimations()
