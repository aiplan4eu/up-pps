from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class ResourceSetResource:
    resourceSetName: str
    resourceCode: str
    resourcePriority: int = 0

    @staticmethod
    def from_dict(obj: Any) -> 'ResourceSetResource':
        _resourceSetName = str(obj.get("resourceSetName"))
        _resourceCode = str(obj.get("resourceCode"))
        #_resourcePriority = int(obj.get("resourcePriority"))
        return ResourceSetResource(_resourceSetName, _resourceCode) # , _resourcePriority)