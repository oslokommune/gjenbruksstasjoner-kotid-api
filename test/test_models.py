import pytest
from datetime import datetime
from dataclasses import asdict
from freezegun import freeze_time

from test.conftest import create_predictions_table
from test.mockdata import test_config_data
from queue_predictions_api.models import (
    PredictionConfig,
    QueuePrediction,
    Station,
)


class TestPredictionConfig:
    def test_ok(self):
        config = {
            "prediction_enabled": True,
            "margin_of_error": 0.25,
            "queue_full_certainty_threshold": 0.9,
            "queue_not_full_certainty_threshold": 0.5,
            "outdated_after_minutes": 15,
        }
        prediction_config = PredictionConfig.from_dict(config)

        assert asdict(prediction_config) == config

    def test_fail(self):
        with pytest.raises(ValueError):
            PredictionConfig.from_dict(
                {
                    "prediction_enabled": True,
                    "margin_of_error": 0.25,
                    "queue_full_certainty_threshold": 1.2,
                    "queue_not_full_certainty_threshold": 0.5,
                    "outdated_after_minutes": 15,
                }
            )

        with pytest.raises(TypeError):
            PredictionConfig.from_dict(
                {
                    "prediction_enabled": True,
                    "margin_of_error": None,
                    "queue_full_certainty_threshold": 0.9,
                    "queue_not_full_certainty_threshold": 0.5,
                    "outdated_after_minutes": 15,
                }
            )

        with pytest.raises(TypeError):
            PredictionConfig.from_dict(
                {"margin_of_error": 0.25, "queue_full_certainty_threshold": 1.2}
            )


class TestQueuePrediction:
    def test_ok(self):
        for values, config, expected in [
            ((0.1, 0.5), (0.25, 0.9, 0.5), (0.5, 0.375, 0.625, False, False)),
            ((0.04, 0.333), (0.25, 0.9, 0.5), (0.333, 0.24975, 0.41625, False, False)),
            ((0.998, 0.765), (0.50, 0.9, 0.3), (0.765, 0.3825, 1.1475, True, False)),
            ((0.72, 0.765), (0.1, 0.9, 0.5), (0.765, 0.6885, 0.8415, None, True)),
        ]:
            prediction = QueuePrediction.from_dict(
                {
                    "station_id": 123,
                    "queue_full": values[0],
                    "expected_queue_time": values[1],
                    "timestamp": 1592480589,
                },
                config=PredictionConfig.from_dict(
                    {
                        "prediction_enabled": True,
                        "margin_of_error": config[0],
                        "queue_full_certainty_threshold": config[1],
                        "queue_not_full_certainty_threshold": config[2],
                        "outdated_after_minutes": 15,
                    }
                ),
            )

            assert asdict(prediction) == {
                "queue_full": values[0],
                "expected_queue_time": values[1],
                "timestamp": 1592480589,
                "config": {
                    "prediction_enabled": True,
                    "margin_of_error": config[0],
                    "queue_full_certainty_threshold": config[1],
                    "queue_not_full_certainty_threshold": config[2],
                    "outdated_after_minutes": 15,
                },
            }

            assert round(prediction.expected_queue_time, 3) == round(expected[0], 3)
            assert round(prediction.min_queue_time, 3) == round(expected[1], 3)
            assert round(prediction.max_queue_time, 3) == round(expected[2], 3)
            assert prediction.is_full is expected[3]
            assert prediction.is_uncertain_prediction is expected[4]

    def test_expiration(self):
        prediction = QueuePrediction.from_dict(
            {
                "station_id": 123,
                "queue_full": 0.1,
                "expected_queue_time": 0.25,
                "timestamp": 1591012800.0,  # 2020-06-01T12:00:00.000Z
            },
            config=PredictionConfig.from_dict(test_config_data["prediction_config"]),
        )

        for time_now, outdated_after_minutes, should_be_outdated in [
            ("2020-06-01T13:05:00+01:00", 15, False),
            ("2020-06-01T13:30:00+01:00", 15, True),
            ("2020-06-01T14:05:00+02:00", 15, False),
            ("2020-06-02T14:05:00+02:00", 15, True),
            ("2020-06-01T14:15:00+02:00", 15, False),
            ("2020-06-01T14:15:01+02:00", 15, True),
            ("2020-06-01T14:10:00+02:00", None, False),
            ("2020-06-01T14:05:00+02:00", 7, False),
            ("2020-06-01T14:10:00+02:00", 7, True),
        ]:
            with freeze_time(time_now):
                prediction.config.outdated_after_minutes = outdated_after_minutes
                assert prediction.is_outdated is should_be_outdated

    def test_invalid_config(self):
        for values, config, expected in [
            ((0.1, 0.5), (1.25, 0.9, 0.5), (0.5, 0.375, 0.625, False, False)),
            ((0.1, 0.5), (0.25, 1.9, 0.5), (0.5, 0.375, 0.625, False, False)),
            ((0.1, 0.5), (0.25, 0.9, 2), (0.5, 0.375, 0.625, False, False)),
        ]:
            with pytest.raises(ValueError):
                QueuePrediction.from_dict(
                    {
                        "station_id": 123,
                        "queue_full": values[0],
                        "expected_queue_time": values[1],
                        "timestamp": 1592480589,
                    },
                    config=PredictionConfig.from_dict(
                        {
                            "prediction_enabled": True,
                            "margin_of_error": config[0],
                            "queue_full_certainty_threshold": config[1],
                            "queue_not_full_certainty_threshold": config[2],
                            "outdated_after_minutes": 15,
                        }
                    ),
                )


class TestStation:
    @freeze_time("2020-06-16T08:55:00+02:00")
    def test_ok(self, mock_dynamodb):
        prediction_timestamp = datetime.timestamp(datetime.now())
        table = create_predictions_table(
            items=[
                {
                    "station_id": 42,
                    "timestamp": prediction_timestamp,
                    "queue_full": 0.04,
                    "expected_queue_time": 0.333,
                }
            ]
        )

        station_config = dict(test_config_data["stations"][42])
        station_config["station_id"] = 42
        station = Station(
            station_id=station_config["station_id"],
            prediction_config=PredictionConfig.from_dict(
                station_config["prediction_config"]
            ),
            station_name=station_config.get("station_name"),
            opening_hours=station_config.get("opening_hours"),
        )

        station_asdict = asdict(station)
        station_asdict.pop("_queue_prediction")

        assert station_asdict == station_config
        assert station.is_open

        station.queue_prediction = table.scan()["Items"][0]

        assert asdict(station.queue_prediction) == {
            "queue_full": 0.04,
            "expected_queue_time": 0.333,
            "timestamp": prediction_timestamp,
            "config": station_config["prediction_config"],
        }

    @freeze_time("2020-06-16T08:55:00+02:00")
    def test_prediction_disabled(self, mock_dynamodb):
        table = create_predictions_table(
            items=[
                {
                    "station_id": 42,
                    "timestamp": datetime.timestamp(datetime.now()),
                    "queue_full": 0.04,
                    "expected_queue_time": 0.333,
                }
            ]
        )

        station_config = dict(test_config_data["stations"][42])
        station_config["station_id"] = 42
        station_config["prediction_config"]["prediction_enabled"] = False
        station = Station(
            station_id=station_config["station_id"],
            prediction_config=PredictionConfig.from_dict(
                station_config["prediction_config"]
            ),
            station_name=station_config.get("station_name"),
            opening_hours=station_config.get("opening_hours"),
        )

        station.queue_prediction = table.scan()["Items"][0]

        assert station.is_open
        assert station._queue_prediction is not None
        assert not station._queue_prediction.is_uncertain_prediction
        assert not station._queue_prediction.is_outdated
        assert not station.prediction_config.prediction_enabled
        assert station.queue_prediction is None

    def test_opening_hours(self):
        station_config = dict(test_config_data["stations"][42])
        station_config["station_id"] = 42
        station = Station(
            station_id=station_config["station_id"],
            prediction_config=PredictionConfig.from_dict(
                station_config["prediction_config"]
            ),
            station_name=station_config.get("station_name"),
            opening_hours=station_config.get("opening_hours"),
        )

        for time_now, should_be_open in [
            ("2020-06-16T08:55:00+02:00", True),  # Tuesday
            ("2020-06-14T12:00:00+02:00", False),  # Sunday
            ("2020-06-17T11:59:59+02:00", True),  # Wednesday; deviation
            ("2020-06-17T12:00:00+02:00", False),  # Wednesday; deviation
            ("2020-06-17T12:00:01+02:00", False),  # Wednesday; deviation
            ("2020-06-20T15:00:00+02:00", True),  # Saturday
            ("2020-06-20T01:00:00+02:00", False),  # Saturday
            ("2020-12-24T12:00:00+02:00", False),  # Thursday; deviation
        ]:
            with freeze_time(time_now):
                assert station.is_open is should_be_open
