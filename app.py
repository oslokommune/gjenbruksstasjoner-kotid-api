import json
import logging
import datetime
from flask import Flask, jsonify
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from queue_estimation_api.queues_endpoint import Queues

logger = logging.getLogger()
logger.setLevel(logging.INFO)


app = Flask(__name__)
api = Api(app)

api.add_resource(Queues, "/", "/<string:station_id>")


@app.errorhandler(HTTPException)
def http_error(e):
    logger.exception(e)

    # Turn default HTML errors pages into JSON
    return jsonify({"message": str(e.description)}), e.code


# TODO: Remove
@app.route("/status")
def status():
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    return json.dumps(app.config, default=default)
