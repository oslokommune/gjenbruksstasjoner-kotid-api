from aws_xray_sdk.core import xray_recorder

# from test.conftest import create_queue_times_table


xray_recorder.begin_segment("Test")


class TestApp:
    def test_queues_endpoint(self, mock_client, mock_dynamodb):
        # table = create_queue_times_table(
        #     items=[]
        # )

        # response = Queues().get(station_id="test-station-id")
        response = mock_client.get("/42")
        # response_data = response.get_json()

        assert response.status_code == 200
