from datetime import datetime

from models import Accident, Participant


def find_accident(
    accidents: list[Accident], accident_id: int
) -> Accident | None:
    return next(
        (
            accident
            for accident in accidents
            if accident.accident_id == accident_id
        ),
        None,
    )


def register_participant(
    accident: Accident, participant: Participant
) -> None:
    accident.add_participant(participant)


def create_accident_message(accident: Accident) -> str:
    emergency_status = (
        "требуется вызов экстренных служб"
        if accident.emergency_required
        else "экстренный вызов не требуется"
    )
    return (
        f"ДТП №{accident.accident_id}\n"
        f"Дата: {accident.occurred_at:%d.%m.%Y %H:%M}\n"
        f"Место: {accident.location}\n"
        f"Категория: {accident.category}\n"
        f"Участников: {len(accident.participants)}\n"
        f"Решение: {emergency_status}"
    )


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "Дата должна быть в формате ГГГГ-ММ-ДДTЧЧ:ММ"
        ) from error
