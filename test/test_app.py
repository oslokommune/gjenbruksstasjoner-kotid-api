from aws_xray_sdk.core import xray_recorder
from freezegun import freeze_time

from test.conftest import create_config_file, create_predictions_table
from test.mockdata import test_config_data, test_prediction_data
from queue_predictions_api.endpoints import station_fields


xray_recorder.begin_segment("Test")


class TestApp:
    def test_get_stations_list(self, mock_client, mock_s3_config, mock_dynamodb):
        create_config_file(test_config_data)
        create_predictions_table(items=[])

        response = mock_client.get("/")
        response_data = response.get_json()

        assert response.status_code == 200
        assert [s["station_id"] for s in response_data] == [
            sid
            for sid, config in test_config_data["stations"].items()
            if config["active"]
        ]
        for station in response_data:
            assert set(station) == set(station_fields)

    @freeze_time("2020-06-01T13:10:00+02:00")
    def test_get_station(self, mock_client, mock_s3_config, mock_dynamodb):
        create_config_file(test_config_data)
        create_predictions_table(items=test_prediction_data.values())

        response = mock_client.get("/41")
        response_data = response.get_json()

        assert response.status_code == 200
        assert response_data == {
            "station_id": 41,
            "station_name": "Grønmo",
            "is_open": True,
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
            "queue": None,
        }

    def test_get_station_no_data(self, mock_client, mock_s3_config):
        def request(station_id):
            response = mock_client.get(f"/{station_id}")
            response_data = response.get_json()

            assert response.status_code == 404
            assert response_data["message"] == "No station data found for provided id"

        request(41)

        create_config_file(test_config_data)

        request(43)
        request(999)
