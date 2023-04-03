from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class ResourceAvailability:
    availabilityStart: int
    availabilityEnd: int
    availabilityType: str

    @staticmethod
    def from_dict(obj: Any) -> 'ResourceAvailability':
        _availabilityStart = int(obj.get("availabilityStart"))
        _availabilityEnd = int(obj.get("availabilityEnd"))
        _availabilityType = str(obj.get("availabilityType"))
        return ResourceAvailability(_availabilityStart, _availabilityEnd, _availabilityType)