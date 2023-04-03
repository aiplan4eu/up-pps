from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class ResourceSet:
    resourceSetName: str

    @staticmethod
    def from_dict(obj: Any) -> 'ResourceSet':
        _resourceSetName = str(obj.get("resourceSetName"))
        return ResourceSet(_resourceSetName)
