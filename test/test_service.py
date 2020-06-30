import json
from decimal import Decimal
from freezegun import freeze_time

from queue_predictions_api.service import QueuePredictionService
from test.conftest import create_config_file, create_predictions_table
from test.mockdata import test_config_data, test_prediction_data


class TestService:
    @freeze_time("2020-06-01T13:10:00+02:00")
    def test_get_station(self, mock_s3_config, mock_dynamodb):
        create_config_file(test_config_data)
        table = create_predictions_table()

        service = QueuePredictionService()

        station = service.get_station(41)
        assert station.queue_prediction is None

        for prediction in test_prediction_data.values():
            table.put_item(Item=json.loads(json.dumps(prediction), parse_float=Decimal))

        station = service.get_station(41)
        assert station.queue_prediction is not None

        station = service.get_station(42)
        assert station.queue_prediction is None

        station = service.get_station(31)
        assert station.queue_prediction is None

    def test_get_all_stations(self, mock_s3_config, mock_dynamodb):
        create_config_file(test_config_data)
        create_predictions_table(items=test_prediction_data.values())

        service = QueuePredictionService()

        stations = service.get_all_stations()

        assert len(stations) == len(
            [s for s in test_config_data["stations"].values() if s["active"]]
        )
