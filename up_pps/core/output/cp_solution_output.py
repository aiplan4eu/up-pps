from dataclasses import dataclass, field
@dataclass
class CPSolutionOutput:
    status: str
    time: float
    objective_name: str
    objective_value: int
    solution_output_list: list = field(default_factory=list)




