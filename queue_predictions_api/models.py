import logging
from pytz import timezone
from typing import List, Optional
from datetime import datetime, time
from dataclasses import dataclass, fields

import queue_predictions_api.data as data


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls, data, **kwargs):
        """ Initialize model instance from dict. Ignores undefined attributes. """
        field_names = set(f.name for f in fields(cls) if f.init is True)
        return cls(**{k: v for k, v in data.items() if k in field_names}, **kwargs)


@dataclass
class PredictionConfig(BaseModel):
    margin_of_error: float
    queue_full_certainty_threshold: float
    queue_not_full_certainty_threshold: float

    def __post_init__(self):
        for field in fields(self):
            if not 0 <= getattr(self, field.name) <= 1:
                raise ValueError()


@dataclass
class QueuePrediction(BaseModel):
    queue_full: float
    expected_queue_time: float
    updated_at: datetime

    config: PredictionConfig

    @property
    def is_uncertain_prediction(self) -> bool:
        """ Determine prediction certainty from configured thresholds. """
        return self.is_full is None

    @property
    def is_full(self) -> Optional[bool]:
        """ Determine queue full probability. Returns None if uncertain. """
        if self.queue_full > self.config.queue_full_certainty_threshold:
            return True

        if self.queue_full < self.config.queue_not_full_certainty_threshold:
            return False

    @property
    def min_queue_time(self) -> float:
        return self.expected_queue_time - (
            self.expected_queue_time * self.config.margin_of_error
        )

    @property
    def max_queue_time(self) -> float:
        return self.expected_queue_time * (1 + self.config.margin_of_error)


@dataclass
class Station(BaseModel):
    station_id: int
    pretty_name: str = None
    opening_hours: dict = None
    prediction_config: dict = None

    @property
    def queue(self) -> Optional[QueuePrediction]:
        if not self.is_open:
            return

        try:
            config = PredictionConfig.from_dict(self.prediction_config)
        except Exception as e:
            logger.error("Error while parsing prediction config")
            logger.exception(e)
            return

        # Get latest prediction data
        prediction_data = data.get_prediction_by_station_id(self.station_id)

        if not prediction_data:
            logger.warning("No prediction data found")
            return

        try:
            prediction = QueuePrediction.from_dict(prediction_data, config=config)
        except Exception as e:
            logger.error("Error while processing prediction data")
            logger.exception(e)
            return

        if prediction.is_uncertain_prediction:
            logger.warning("Prediction is too uncertain")
            return

        return prediction

    @property
    def is_open(self) -> bool:
        if not self.opening_hours:
            logger.warning("No opening hours config defined for requested station")
            return False

        now = datetime.now(timezone("Europe/Oslo"))

        try:
            hours = self._get_hours(now)
        except Exception as e:
            logger.exception(e)
            return False

        if not hours:
            return False

        try:
            return self._time_in_range(
                time=now.time(),
                start=datetime.strptime(hours["open"], "%H:%M").time(),
                end=datetime.strptime(hours["closed"], "%H:%M").time(),
            )
        except Exception as e:
            logger.exception(e)

        return False

    def _get_hours(self, datetime: datetime) -> Optional[dict]:
        now_date = datetime.strftime("%Y-%m-%d")

        if now_date in self.opening_hours.get("deviations", {}):
            return self.opening_hours["deviations"][now_date]

        now_weekday = datetime.strftime("%A").lower()
        opening_hours = {k.lower(): v for k, v in self.opening_hours.items()}

        return opening_hours.get(now_weekday, opening_hours.get("default"))

    def _time_in_range(self, time: time, start: time, end: time) -> bool:
        if start < end:
            return start <= time < end

        return False


@dataclass(init=False)
class Config(BaseModel):
    prediction_config: dict
    stations: dict

    def __init__(self):
        config = data.get_config()
        self.prediction_config = config["prediction_config"]
        self.stations = config["stations"]

    def get_station(self, station_id) -> Optional[Station]:
        if station_id not in self.stations or not self.stations[station_id].get(
            "active", False
        ):
            return None

        # Update defaults
        station_config = {
            "station_id": station_id,
            "prediction_config": self.prediction_config,
        }
        station_config.update(self.stations[station_id])

        try:
            return Station.from_dict(station_config)
        except Exception as e:
            logger.exception(e)
            raise

    def get_all_stations(self) -> List[Station]:
        return list(
            filter(
                lambda s: s is not None,
                [self.get_station(station_id) for station_id in self.stations.keys()],
            )
        )
