import pytest
from aws_xray_sdk.core import xray_recorder

from app import app as flask_app
from queue_estimation_api.queues_endpoint import Queues


xray_recorder.begin_segment("Test")


@pytest.fixture
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flask_app.config["TESTING"] = True

    with flask_app.test_client() as client:
        # with flaskr.app.app_context():
        #     flaskr.init_db()
        yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])


class TestApp:
    def test_queue(self, client):
        # response = Queues().get(station_id="test-station-id")
        response = client.get("/")

        assert response.status_code == 200

        print(response.get_json())

        assert False

        """
        assert dict(response) == {
            "station_id": "station_id_41_20200506T103000.bin",
            "predicted_queue_time": 10.6,
            "updated_at": "2020-06-05T09:05:12.802129",
        }
        """
