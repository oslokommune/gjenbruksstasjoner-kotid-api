import json
import datetime
import logging.config
from flask import Flask, jsonify
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from queue_predictions_api.endpoints import StationListResource, StationResource


logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
            },
        },
        "handlers": {
            "stream": {"class": "logging.StreamHandler", "formatter": "standard"}
        },
        "loggers": {
            "werkzeug": {"level": "INFO", "handlers": ["stream"], "propagate": True},
            "queue_predictions_api": {
                "level": "INFO",
                "handlers": ["stream"],
                "propagate": True,
            },
        },
    }
)

app = Flask("queue_predictions_api")
api = Api(app)

api.add_resource(StationListResource, "/")
api.add_resource(StationResource, "/<int:station_id>")


@app.after_request
def after_request(response):
    # Alt. https://flask-cors.readthedocs.io/en/latest/
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    return response


@app.errorhandler(HTTPException)
def http_error(e):
    app.logger.exception(e)

    # Turn default HTML errors pages into JSON
    return jsonify({"message": str(e.description)}), e.code


# TODO: Remove
@app.route("/status")
def status():
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    return json.dumps(app.config, default=default)
