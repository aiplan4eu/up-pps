from typing import List
from typing import Any
from dataclasses import dataclass, field


@dataclass
class ActivityFact:
    activityCode: str
    activityPriority: int
    activityProcessingTime: int
    activityReleaseTime: int
    activityDueTime: int
    resourceSetList: list = field(default_factory=list)
    seizeReleaseAndResourceSet: dict = field(default_factory=dict)

    def add_resource_set_list(self, resource_set_list):
        self.resourceSetList.extend(resource_set_list)

    def add_resource_set_to_list(self, resource_set):
        self.resourceSetList.append(resource_set)

    def add_seize_release_resource_set_to_map(self, seize_release_name, resource_set_name):
        self.seizeReleaseAndResourceSet[seize_release_name] = resource_set_name

    def __hash__(self) -> int:
        return super().__hash__()


