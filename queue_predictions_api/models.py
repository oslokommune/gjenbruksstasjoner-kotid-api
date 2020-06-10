from datetime import datetime
from dataclasses import dataclass, fields


@dataclass(init=False)
class PredictionConfig:
    margin_of_error: float
    queue_full_certainty_threshold: float
    queue_not_full_certainty_threshold: float

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for key, value in kwargs.items():
            if key not in names:
                continue

            if not 0 <= value <= 1:
                raise ValueError()

            setattr(self, key, value)


@dataclass
class StationQueue:
    config: PredictionConfig

    station_id: int
    expected_queue_time: int
    queue_full: bool
    updated_at: datetime = None  # TODO: From DB
    # station_name: str = "Heisann"  # TODO: From config?

    @property
    def is_open(self):
        # TODO: From config?
        return True

    @property
    def is_queue_full(self):
        if self.queue_full > self.config.queue_full_certainty_threshold:
            return True

        if self.queue_full < self.config.queue_not_full_certainty_threshold:
            return False

    @property
    def is_uncertain_prediction(self):
        return self.is_queue_full is None

    @property
    def queue_prediction(self):
        # Do not return prediction if closed or too uncertain
        if not self.is_open or self.is_uncertain_prediction:
            return None

        return {
            "is_full": self.is_queue_full,
            "expected_time": self.expected_queue_time,
            "min_time": (
                self.expected_queue_time
                - (self.expected_queue_time * self.config.margin_of_error)
            ),
            "max_time": (self.expected_queue_time * (1 + self.config.margin_of_error)),
        }
