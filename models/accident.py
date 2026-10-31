from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Accident:
    accident_id: int
    location: str
    occurred_at: datetime
    has_injured: bool = False
    has_fire: bool = False
    status: str = "new"
    participants: list["Participant"] = field(default_factory=list)

    @property
    def emergency_required(self) -> bool:
        return self.has_injured or self.has_fire

    @property
    def category(self) -> str:
        if self.emergency_required:
            return "Повышенная опасность"
        if len(self.participants) > 2:
            return "Массовое ДТП"
        return "Без пострадавших"

    def add_participant(self, participant: "Participant") -> None:
        if participant not in self.participants:
            self.participants.append(participant)

    def __str__(self) -> str:
        return f"ДТП №{self.accident_id}: {self.location} ({self.category})"


from .participant import Participant  # noqa: E402
