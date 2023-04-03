from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class Parameter:
    parameterName: str
    parameterValue: str

    @staticmethod
    def from_dict(obj: Any) -> 'Parameter':
        _parameterName = str(obj.get("parameterName"))
        _parameterValue = str(obj.get("parameterValue"))
        return Parameter(_parameterName, _parameterValue)