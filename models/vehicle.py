from dataclasses import dataclass


@dataclass
class Vehicle:
    vehicle_id: int
    plate_number: str
    brand: str
    model: str

    def __str__(self) -> str:
        return f"{self.brand} {self.model} ({self.plate_number})"
