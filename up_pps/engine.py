

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


    @property
    def name(self) -> str:
        return 'PPS'

    @staticmethod
    def supported_kind() -> ProblemKind:
        supported_kind = ProblemKind()
        supported_kind.set_problem_class('SCHEDULING') # type: ignore
        #### COMPLETE
        return

    @staticmethod
    def supports(problem_kind: 'up.model.ProblemKind') -> bool:
        return problem_kind <= EngineImpl.supported_kind()


    def _solve(self, problem: 'up.model.AbstractProblem',
               heuristic: Optional[Callable[["up.model.state.ROState"], Optional[float]]] = None,
               timeout: Optional[float] = None,
               output_stream: Optional[IO[str]] = None) -> 'up.engines.results.PlanGenerationResult':
        assert isinstance(problem, up.model.Problem)
        if timeout is not None:
            warnings.warn('PPS does not support timeout.', UserWarning)
        if output_stream is not None:
            warnings.warn('PPS does not support output stream.', UserWarning)
        scheduling_pbm = self._convert_problem(problem)
        instance_manager = scheduling_pbm.build_instance_manager()
        cp_model_opt = CpModel()
        cp_model_opt.build_model(instance_manager)
        cp_model_opt.run_model()
        plan = cp_model_opt.build_plan
        up_plan = self._to_up_plan(problem,plan)

        return up_plan



    def _convert_problem(self, problem: 'up.model.Problem'):

        converter = Converter(problem)
        scheduling_problem = converter.build_scheduling_problem()

        return scheduling_problem

    def _to_up_plan(self, problem: 'up.model.Problem',
                    plan: Optional[pps_plan]):
        if ttplan is None:
            return None
        converter = Converter(problem)
        up_plan = converter.build_up_plan(pps_plan)

        return up_plan #up.plans.SequentialPlan([a[1] for a in actions], problem.env)

