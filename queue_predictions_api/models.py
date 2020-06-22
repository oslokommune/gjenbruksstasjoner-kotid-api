import pytz
import logging
from typing import Optional
from datetime import datetime, time
from dataclasses import dataclass, fields


logger = logging.getLogger("queue_predictions_api.models")


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
    timestamp: float

    config: PredictionConfig

    def __post_init__(self):
        self.queue_full = float(self.queue_full)
        self.expected_queue_time = float(self.expected_queue_time)
        self.timestamp = float(self.timestamp)

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
        return self.expected_queue_time * (1 - self.config.margin_of_error)

    @property
    def max_queue_time(self) -> float:
        return self.expected_queue_time * (1 + self.config.margin_of_error)

    @property
    def updated_at(self) -> datetime:
        dt = datetime.fromtimestamp(self.timestamp, tz=pytz.timezone("Europe/Oslo"))
        return dt


@dataclass
class Station(BaseModel):
    station_id: int
    prediction_config: PredictionConfig
    station_name: str = None
    opening_hours: dict = None

    _queue_prediction: QueuePrediction = None

    @property
    def queue_prediction(self) -> Optional[QueuePrediction]:
        if not self._queue_prediction or not self.is_open:
            return

        if self._queue_prediction.is_uncertain_prediction:
            logger.warning(f"Prediction for station {self.station_id} is too uncertain")
            return

        return self._queue_prediction

    @queue_prediction.setter
    def queue_prediction(self, prediction_data: dict):
        if not prediction_data:
            self._queue_prediction = None
            return

        try:
            self._queue_prediction = QueuePrediction.from_dict(
                prediction_data, config=self.prediction_config
            )
        except Exception as e:
            logger.error("Error while processing prediction data")
            logger.exception(e)
            self._queue_prediction = None

    @property
    def is_open(self) -> bool:
        if not self.opening_hours:
            logger.warning(
                f"No opening hours config defined for station {self.station_id}"
            )
            return False

        now = datetime.now(pytz.timezone("Europe/Oslo"))

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
