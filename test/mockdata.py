test_config_data = {
    "prediction_config": {
        "margin_of_error": 0.25,
        "queue_full_certainty_threshold": 0.9,
        "queue_not_full_certainty_threshold": 0.5,
    },
    "stations": {
        41: {
            "active": True,
            "station_name": "Grønmo",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
            },
        },
        42: {
            "active": True,
            "station_name": "Haraldrud gjenbruksstasjon",
            "opening_hours": {
                "default": {"open": "07:00", "closed": "21:00"},
                "saturday": {"open": "07:00", "closed": "17:00"},
                "sunday": None,
                "deviations": {
                    "2020-12-24": None,
                    "2020-06-11": {"open": "08:00", "closed": "16:00"},
                    "2020-06-17": {"open": "08:00", "closed": "12:00"},
                },
            },
            "prediction_config": {
                "margin_of_error": 0.3,
                "queue_full_certainty_threshold": 0.9,
                "queue_not_full_certainty_threshold": 0.5,
            },
        },
        43: {
            "active": False,
            "station_name": "Smestad",
            "opening_hours": {},
            "prediction_config": {},
        },
        44: {
            "active": True,
            "station_name": "Heggvin",
            "opening_hours": {},
            "prediction_config": {},
        },
        45: {"active": True},
    },
}

test_prediction_data = {
    41: {
        "station_id": 41,
        "queue_full": 0.1,
        "expected_queue_time": 0.5,
        "timestamp": 1591009200.0,  # 2020-06-01 11:00:00
    },
    42: {
        "station_id": 42,
        "queue_full": 0.74,  # UNCERTAIN
        "expected_queue_time": 0.712,
        "timestamp": 1591012800.0,  # 2020-06-01 12:00:00
    },
}