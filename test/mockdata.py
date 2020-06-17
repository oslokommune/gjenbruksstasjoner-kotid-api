from datetime import datetime


test_config_data = {
    "prediction_config": {
        "margin_of_error": 0.25,
        "queue_full_certainty_threshold": 0.9,
        "queue_not_full_certainty_threshold": 0.5,
    },
    "stations": {
        41: {
            "active": True,
            "pretty_name": "Grønmo",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
            },
        },
        42: {
            "active": True,
            "pretty_name": "Haraldrud gjenbruksstasjon",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
                "deviations": {
                    "2020-12-24": None,
                    "2020-06-11": {"open": "08:00", "closed": "16:00"},
                },
            },
            "prediction_config": {
                "margin_of_error": 0.3,
                "queue_full_certainty_threshold": 0.9,
                "queue_not_full_certainty_threshold": 0.5,
            },
        },
    },
}
test_prediction_data = {
    41: {
        "station_id": 41,
        "queue_full": 0.1,
        "expected_queue_time": 0.5,
        "timestamp": datetime.timestamp(datetime.now()),
    },
    42: {
        "station_id": 42,
        "queue_full": 0.74,  # UNCERTAIN
        "expected_queue_time": 0.333,
        "timestamp": datetime.timestamp(datetime.now()),
    },
}
