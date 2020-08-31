from aws_xray_sdk.core import xray_recorder
from freezegun import freeze_time

from test.conftest import create_config_file, create_predictions_table
from queue_predictions_api.endpoints import station_fields
from queue_predictions_api.service import QueuePredictionService


xray_recorder.begin_segment("Test")


class TestApp:
    def test_get_stations_list(
        self, mock_client, mock_s3_config, mock_dynamodb, config_data
    ):
        create_config_file(config_data)
        create_predictions_table(items=[])

        response = mock_client.get("/")
        response_data = response.get_json()

        service = QueuePredictionService()

        assert response.status_code == 200
        assert set([s["station_id"] for s in response_data]) == set(
            [s.station_id for s in service.get_all_stations()]
        )
        for station in response_data:
            assert set(station) == set(station_fields)

    @freeze_time("2020-06-01T13:10:00+02:00")
    def test_get_station(
        self, mock_client, mock_s3_config, mock_dynamodb, prediction_data, config_data
    ):
        create_config_file(config_data)
        create_predictions_table(items=prediction_data.values())

        response = mock_client.get("/41")
        response_data = response.get_json()

        assert response.status_code == 200
        assert response_data == {
            "station_id": 41,
            "station_name": "Grønmo",
            "is_open": True,
            "show_station": True,
            "queue_prediction_enabled": True,
            "queue": {
                "expected_time": 0.5,
                "is_full": False,
                "max_time": 0.625,
                "min_time": 0.375,
                "updated_at": "2020-06-01T13:00:00+02:00",
            },
        }

        response = mock_client.get("/42")
        response_data = response.get_json()

        assert response.status_code == 200

        assert response_data == {
            "station_id": 42,
            "station_name": "Haraldrud gjenbruksstasjon",
            "is_open": True,
            "show_station": True,
            "queue_prediction_enabled": True,
            "queue": None,
        }

        response = mock_client.get("/43")
        response_data = response.get_json()

        assert response.status_code == 200
        assert response_data["station_id"] == 43
        assert not response_data["show_station"]

    def test_get_station_no_data(self, mock_client, mock_s3_config, config_data):
        def request(station_id):
            response = mock_client.get(f"/{station_id}")
            response_data = response.get_json()

            assert response.status_code == 404
            assert response_data["message"] == "No station data found for provided id"

        request(41)

        create_config_file(config_data)

        request(999)
