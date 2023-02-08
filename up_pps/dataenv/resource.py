from typing import List
from typing import Any
from dataclasses import dataclass, field
from scheduling.dataenv.resource_availability import ResourceAvailability


@dataclass
class Resource:
    resourceCode: str
    resourceAvailabilityList: list = field(default_factory=list)

    @staticmethod
    def from_dict(obj: Any) -> 'Resource':
        _resourceCode = str(obj.get("resourceCode"))
        _resourceAvailabilityList = [ResourceAvailability.from_dict(y) for y in obj.get("resourceAvailabilityList")]
        return Resource(_resourceCode, _resourceAvailabilityList)

    def add_availability_list(self, list):
        self.resourceAvailabilityList = list
