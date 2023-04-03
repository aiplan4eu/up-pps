from dataclasses import dataclass, field


@dataclass
class SolutionOutput:
    activity_name: str
    activity_start: int
    activity_end: int
    resource_name_by_resource_set_name: dict = field(default_factory=dict)




