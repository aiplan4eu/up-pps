from typing import List
from typing import Any
from dataclasses import dataclass, field


@dataclass
class Activity:
    activityCode: str
    activityProcessingTime: int
    activityReleaseTime: int
    activityDueTime: int
    activityPriority: int = 1

    @staticmethod
    def from_dict(obj: Any) -> 'Activity':
        _activityCode = str(obj.get("activityCode"))
        _activityPriority = str(obj.get("activityPriority"))
        _activityProcessingTime = int(obj.get("activityProcessingTime"))
        _activityReleaseTime = int(obj.get("activityReleaseTime"))
        _activityDueTime = int(obj.get("activityDueTime"))
        return Activity(_activityCode, _activityProcessingTime, _activityReleaseTime, _activityDueTime, _activityPriority)