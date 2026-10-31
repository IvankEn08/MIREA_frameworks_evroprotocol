from dataclasses import dataclass

from .vehicle import Vehicle


@dataclass
class Participant:
    participant_id: int
    full_name: str
    phone: str
    vehicle: Vehicle

    def __str__(self) -> str:
        return f"{self.full_name}, {self.vehicle}"
