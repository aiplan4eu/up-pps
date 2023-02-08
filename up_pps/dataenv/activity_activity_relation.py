from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class ActivityActivityRelation:
    firstActivityCode: str
    secondActivityCode: str
    relationType: str
    relationWindowMin: int = 0
    relationWindowMax: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'ActivityActivityRelation':
        _firstActivityCode = str(obj.get("firstActivityCode"))
        _secondActivityCode = str(obj.get("secondActivityCode"))
        _relationType = str(obj.get("relationType"))
        _relationWindowMin = int(obj.get("relationWindowMin"))
        _relationWindowMax = int(obj.get("relationWindowMax"))
        return ActivityActivityRelation(_firstActivityCode, _secondActivityCode, _relationType, _relationWindowMin, _relationWindowMax)
