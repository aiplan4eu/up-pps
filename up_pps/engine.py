
import sys
import warnings
import unified_planning as up
import unified_planning.plans
import unified_planning.engines
import unified_planning.engines.mixins
import up_pps
from unified_planning.model import ProblemKind
from unified_planning.engines import PlanGenerationResultStatus, ValidationResult, ValidationResultStatus, Credits
from up_pps import converter
from up_pps.converter import Converter
from up_pps.core.cp_solver import CpModel
from up_pps.manager.instance_manager import InstanceManager
from typing import IO, Callable, Optional, Dict, List, Tuple, Union, Set, cast


class EngineImplementation(
        up.engines.Engine,
        up.engines.mixins.OneshotPlannerMixin
    ):
    def __init__(self):
        up.engines.Engine.__init__(self)
        up.engines.mixins.OneshotPlannerMixin.__init__(self)
        self.setupMap = None
        self.param_map = None
        self.resource_list = None
        self.activity_due_time = None
        self.activity_release_time = None
        self.activity_processing_time = None
        self.activity_resource_compatibility = None
        self.resource_index_by_resource_name = {}
        self.activity_index_by_activity_name = {}
        self.n_resource = None
        self.n_activity = None
        self.activity_list = []
        self.activity_relation_list = []
        self.resource_list_by_resource_set = {}
        self.resource_unavailability_map = {}
        self.T = None
        self.converter = None


    @property
    def name(self) -> str:
        return 'PPS'

    @staticmethod
    def supported_kind() -> ProblemKind:
        supported_kind = ProblemKind()
        supported_kind.set_problem_class("SCHEDULING") # type: ignore
        #### COMPLETE
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'up.model.ProblemKind') -> bool:
        return problem_kind <= EngineImplementation.supported_kind()


    def _solve(self, problem: 'up.model.AbstractProblem',
               heuristic: Optional[Callable[["up.model.state.ROState"], Optional[float]]] = None,
               timeout: Optional[float] = None,
               output_stream: Optional[IO[str]] = None) -> 'up.engines.results.PlanGenerationResult':
        assert isinstance(problem, up.model.scheduling.SchedulingProblem)
        if output_stream is not None:
            warnings.warn('PPS does not support output stream.', UserWarning)
        scheduling_pbm = self._convert_input_problem(problem)
        instance_manager = InstanceManager()
        instance_manager.build_instance_manager(scheduling_pbm)
        instance_manager.parameter_map["TIME_LIMIT"] = timeout if timeout is not None else 60
        cp_model_opt = CpModel()
        cp_model_opt.build_model(instance_manager)
        solution = cp_model_opt.run_model()
        up_plan = self._convert_output_problem(solution)

        return up.engines.PlanGenerationResult(
            PlanGenerationResultStatus.UNSOLVABLE_PROVEN if up_plan is None else PlanGenerationResultStatus.SOLVED_SATISFICING,
            up_plan, self.name)

    def _convert_input_problem(self, problem: 'up.model.Problem'):

        self.converter = Converter(problem)
        scheduling_problem = self.converter.build_scheduling_problem()

        return scheduling_problem

    def _convert_output_problem(self, solution: 'up_pps.core.output.CPOutputModel'):

        up_plan = self.converter.build_up_plan(solution)

        return up_plan
