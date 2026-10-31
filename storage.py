import json
from datetime import datetime
from pathlib import Path

from models import Accident, Participant, Vehicle


def load_accidents(path: str | Path) -> list[Accident]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    try:
        raw_data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в файле {file_path}") from error

    accidents: list[Accident] = []
    for item in raw_data:
        participants = []
        for participant_data in item.get("participants", []):
            vehicle_data = participant_data["vehicle"]
            vehicle = Vehicle(**vehicle_data)
            participants.append(
                Participant(vehicle=vehicle, **{
                    key: value
                    for key, value in participant_data.items()
                    if key != "vehicle"
                })
            )
        accidents.append(
            Accident(
                accident_id=item["accident_id"],
                location=item["location"],
                occurred_at=datetime.fromisoformat(item["occurred_at"]),
                has_injured=item["has_injured"],
                has_fire=item["has_fire"],
                status=item.get("status", "new"),
                participants=participants,
            )
        )
    return accidents


def save_accidents(
    path: str | Path, accidents: list[Accident]
) -> None:
    payload = []
    for accident in accidents:
        participants = []
        for participant in accident.participants:
            participants.append(
                {
                    "participant_id": participant.participant_id,
                    "full_name": participant.full_name,
                    "phone": participant.phone,
                    "vehicle": {
                        "vehicle_id": participant.vehicle.vehicle_id,
                        "plate_number": participant.vehicle.plate_number,
                        "brand": participant.vehicle.brand,
                        "model": participant.vehicle.model,
                    },
                }
            )
        payload.append(
            {
                "accident_id": accident.accident_id,
                "location": accident.location,
                "occurred_at": accident.occurred_at.isoformat(),
                "has_injured": accident.has_injured,
                "has_fire": accident.has_fire,
                "status": accident.status,
                "participants": participants,
            }
        )
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
