from datetime import datetime

import pytest

from models import Accident, Participant, Vehicle
from services import create_accident_message, parse_datetime
from storage import load_accidents, save_accidents


def test_accident_requires_emergency_for_injured_person():
    accident = Accident(1, "Москва", datetime.now(), has_injured=True)
    assert accident.emergency_required is True
    assert accident.category == "Повышенная опасность"


def test_participant_changes_accident_category():
    accident = Accident(1, "Москва", datetime.now())
    for index in range(3):
        vehicle = Vehicle(index, f"A{index}", "Brand", "Model")
        accident.add_participant(
            Participant(index, f"Участник {index}", "+7", vehicle)
        )
    assert accident.category == "Массовое ДТП"


def test_message_contains_project_data():
    accident = Accident(7, "Бауманская", datetime(2026, 10, 20, 10, 30))
    message = create_accident_message(accident)
    assert "ДТП №7" in message
    assert "Бауманская" in message


def test_invalid_datetime_has_clear_error():
    with pytest.raises(ValueError, match="ГГГГ-ММ-ДД"):
        parse_datetime("20.10.2026")


def test_json_roundtrip(tmp_path):
    path = tmp_path / "accidents.json"
    accidents = [Accident(1, "Москва", datetime(2026, 10, 20, 10, 30))]
    save_accidents(path, accidents)
    loaded = load_accidents(path)
    assert loaded[0].location == "Москва"
    assert loaded[0].occurred_at == datetime(2026, 10, 20, 10, 30)
