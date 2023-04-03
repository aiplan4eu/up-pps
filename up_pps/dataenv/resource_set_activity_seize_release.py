from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class ResourceSetActivitySeizeRelease:
    seizeReleaseName: str
    seizeReleaseResourceSetName: str
    seizeReleaseSeizingActivityCode: str
    seizeReleaseReleasingActivityCode: str

    @staticmethod
    def from_dict(obj: Any) -> 'ResourceSetActivitySeizeRelease':
        _seizeReleaseName = str(obj.get("seizeReleaseName"))
        _seizeReleaseResourceSetName = str(obj.get("seizeReleaseResourceSetName"))
        _seizeReleaseSeizingActivityCode = str(obj.get("seizeReleaseSeizingActivityCode"))
        _seizeReleaseReleasingActivityCode = str(obj.get("seizeReleaseReleasingActivityCode"))
        return ResourceSetActivitySeizeRelease(_seizeReleaseName, _seizeReleaseResourceSetName, _seizeReleaseSeizingActivityCode, _seizeReleaseReleasingActivityCode)

    def __hash__(self) -> int:
        return super().__hash__()


