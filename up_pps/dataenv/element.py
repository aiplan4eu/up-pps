from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class Element:
    elementId: str
    elementProductionProcessName: str
    elementOrderName: str = 'default_order_name'

    @staticmethod
    def from_dict(obj: Any) -> 'Element':
        _elementId = str(obj.get("elementId"))
        _elementProductionProcessName = str(obj.get("elementProductionProcessName"))
        _elementOrderName = str(obj.get("elementOrderName"))
        return Element(_elementId, _elementProductionProcessName, _elementOrderName)
