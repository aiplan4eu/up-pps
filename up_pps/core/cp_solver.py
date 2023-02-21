from functools import reduce
from itertools import chain
from operator import xor
import numpy as np
import itertools

from ortools.sat.python import cp_model


class CpModel:

    def __init__(self):

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

    def build_model(self, instance_manager):

        self.n_activity = len(instance_manager.activity_fact_list)
        self.n_resource = len(instance_manager.resource_list)

        for activity_index in range(self.n_activity):
            self.activity_index_by_activity_name[
                instance_manager.activity_fact_list[activity_index].activityCode] = activity_index

        for resource_index in range(self.n_resource):
            self.resource_index_by_resource_name[
                instance_manager.resource_list[resource_index].resourceCode] = resource_index

        self.activity_resource_compatibility = np.zeros([self.n_activity, self.n_resource])
        self.activity_processing_time = np.zeros(self.n_activity, dtype='int')
        self.activity_release_time = np.zeros(self.n_activity, dtype='int')
        self.activity_due_time = np.zeros(self.n_activity, dtype='int')
        self.param_map = instance_manager.parameter_map
        self.T = int(self.param_map['HORIZON'])
        self.param_map = instance_manager.parameter_map
        self.resource_list_by_resource_set = instance_manager.resource_list_by_resource_set

        for activity in instance_manager.activity_fact_list:
            a = self.activity_index_by_activity_name[activity.activityCode]
            self.activity_release_time[a] = activity.activityReleaseTime
            self.activity_due_time[a] = activity.activityDueTime
            self.activity_processing_time[a] = activity.activityProcessingTime
            for resourceSet in activity.resourceSetList:
                for resource in self.resource_list_by_resource_set[resourceSet]:
                    r = self.resource_index_by_resource_name[resource.resourceCode]
                    self.activity_resource_compatibility[a][r] = 1

        self.activity_list = instance_manager.activity_fact_list
        self.activity_relation_list = instance_manager.activity_relation_list
        self.resource_list = instance_manager.resource_list

        # if the resource has availabilities, we insert it in a map with as key the resource code and as values
        # the intervals of unavailability
        for resource in self.resource_list:
            if resource.resourceAvailabilityList is not None:
                availability_shift = []
                for availability in resource.resourceAvailabilityList:
                    if not resource.resourceCode in self.resource_unavailability_map.keys():
                        self.resource_unavailability_map[resource.resourceCode] = []
                    if availability.availabilityType == "UNAVAILABLE":
                        if availability.availabilityEnd <= self.T:
                            self.resource_unavailability_map[resource.resourceCode].append(
                                [availability.availabilityStart, availability.availabilityEnd])
                        elif availability.availabilityStart < self.T < availability.availabilityEnd:
                            self.resource_unavailability_map[resource.resourceCode].append(
                                [availability.availabilityStart, self.T])
                    elif availability.availabilityType == "AVAILABLE":
                        if availability.availabilityEnd <= self.T:
                            availability_shift.append([availability.availabilityStart, availability.availabilityEnd])
                        elif availability.availabilityStart < self.T < availability.availabilityEnd:
                            availability_shift.append([availability.availabilityStart, self.T])
                if len(availability_shift) > 0:
                    # if there are some intervals of availability, from the time horizon we deduct the unavailability intervals
                    horizon = [[0, self.T]]
                    unavailability_shift_temp = sorted((reduce(xor, map(set, chain(horizon, availability_shift)))))
                    unavailability_shift = []
                    for i in range(0, len(unavailability_shift_temp), 2):
                        unavailability_shift.append(unavailability_shift_temp[i:i + 2])
                    self.resource_unavailability_map[resource.resourceCode].extend(unavailability_shift)

        self.setupMap = instance_manager.setup_time_map

    def run_model(self):

        # variables
        model = cp_model.CpModel()
        start_activity = {}
        end_activity = {}
        interval_activity = {}
        assigned_activity_to_resource_of_resource_set = {}
        start_activity_to_resource_of_resource_set = {}
        end_activity_to_resource_of_resource_set = {}
        interval_activity_to_resource = {}
        duration_activity_to_resource = {}


        # init variables
        for activity in self.activity_list:
            a = self.activity_index_by_activity_name[activity.activityCode]
            start_activity[a] = model.NewIntVar(activity.activityReleaseTime, activity.activityDueTime if activity.activityDueTime!=2147483647 else self.T,
                                                'start_activity%i' % a)
            end_activity[a] = model.NewIntVar(activity.activityReleaseTime, activity.activityDueTime if activity.activityDueTime!=2147483647 else self.T,
                                              'end_activity%i' % a)
            interval_activity[a] = model.NewIntervalVar(start_activity[a], self.activity_processing_time[a],
                                                        end_activity[a],
                                                        'interval_activity%i' % a)
            for resourceSetName in activity.resourceSetList:
                for resource in self.resource_list_by_resource_set.get(resourceSetName):
                    r = self.resource_index_by_resource_name[resource.resourceCode]
                    if self.activity_resource_compatibility[a][r] == 1:
                        assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)] = model.NewBoolVar(
                            'assigned_activity%i_to_resource%i_of_resource_set%s' % (a, r, resourceSetName))
                        start_activity_to_resource_of_resource_set[(a, r, resourceSetName)] = model.NewIntVar(
                            activity.activityReleaseTime,
                            activity.activityDueTime,
                            'start_activity%i_to_resource%i_of_resource_set%s' % (a, r, resourceSetName))
                        end_activity_to_resource_of_resource_set[(a, r, resourceSetName)] = model.NewIntVar(
                            activity.activityReleaseTime,
                            activity.activityDueTime,
                            'end_activity%i_to_resource%i_of_resource_set%s' % (a, r, resourceSetName))
                        duration_activity_to_resource[(a, r)] = model.NewIntVar(0, self.activity_processing_time[a],
                                                                                'duration_activity%i_to_resource%i' % (
                                                                                     a, r))
                        # interval_activity_to_resource[(a, r, resourceSetName)] = model.NewIntervalVar(
                        #     start_activity_to_resource_of_resource_set[(a, r, resourceSetName)],
                        #     duration_activity_to_resource[(a, r)],
                        #     end_activity_to_resource_of_resource_set[(a, r, resourceSetName)],
                        #     'interval_activity%i_to_resource%i_of_resource_set%s' % (a, r, resourceSetName))

                        interval_activity_to_resource[(a, r, resourceSetName)] = model.NewOptionalIntervalVar(
                            start_activity_to_resource_of_resource_set[(a, r, resourceSetName)],
                            duration_activity_to_resource[(a, r)],
                            end_activity_to_resource_of_resource_set[(a, r, resourceSetName)],
                            assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)],
                            'interval_activity%i_to_resource%i_of_resource_set%s' % (a, r, resourceSetName))

        for activity in self.activity_list:
            a = self.activity_index_by_activity_name[activity.activityCode]
            for resourceSetName in activity.resourceSetList:
                for resource in self.resource_list_by_resource_set.get(resourceSetName):
                    r = self.resource_index_by_resource_name.get(resource.resourceCode)
                    if self.activity_resource_compatibility[a][r] == 1:
                        # constraint:the end of the activity processed with a resource must be >= of the activity release time + its processing time
                        # and equal to start activity with that resource + its processing time
                        model.Add(end_activity_to_resource_of_resource_set[(a, r, resourceSetName)] >=
                                  self.activity_release_time[a] +
                                  self.activity_processing_time[a])
                        model.Add(end_activity_to_resource_of_resource_set[(a, r, resourceSetName)] ==
                                  start_activity_to_resource_of_resource_set[(a, r, resourceSetName)] +
                                  self.activity_processing_time[a])
                        # constraint: if resource r is assigned to activity t the start and end of the activity correspond to start and end of activity to resource
                        model.Add(
                            start_activity[a] == start_activity_to_resource_of_resource_set[(a, r, resourceSetName)]) \
                            .OnlyEnforceIf(assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)])
                        model.Add(end_activity[a] == end_activity_to_resource_of_resource_set[(a, r, resourceSetName)]) \
                            .OnlyEnforceIf(assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)])

                        # constraint: duration_activity_to_resource is equal to activity_processing time if assigned, zero otherwise
                        model.Add(duration_activity_to_resource[(a, r)] ==
                                  self.activity_processing_time[a]).OnlyEnforceIf(
                            assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)])

            # constraint : verify that one resource per resource set is assigned to an activity if an activity has
            # more than one seize_release picking from the same resource set. we verify that the activity employs n
            # resources with n = number of seize_release picking from the resource set

            for resourceSetName in set(activity.resourceSetList):
                assigned_list = []
                for resource in self.resource_list_by_resource_set.get(resourceSetName):
                    r = self.resource_index_by_resource_name.get(resource.resourceCode)
                    if self.activity_resource_compatibility[a][r] == 1:
                        assigned_list.append(assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)])
                times_resource_set_in_activity = activity.resourceSetList.count(resourceSetName)
                model.Add(cp_model.LinearExpr.Sum(assigned_list) == times_resource_set_in_activity)

        # constraint : we check no overlapping for the resource employment + unavailability intervals

        for resource_set_name in self.resource_list_by_resource_set.keys():
            for resource in self.resource_list_by_resource_set[resource_set_name]:
                r = self.resource_index_by_resource_name[resource.resourceCode]
                intervals = []
                for activity in filter(lambda aa: resource_set_name in aa.resourceSetList, self.activity_list):
                    a = self.activity_index_by_activity_name[activity.activityCode]
                    intervals.append(interval_activity_to_resource[(a, r, resource_set_name)])

                if self.resource_unavailability_map.get(resource.resourceCode) is not None:
                    for interval in self.resource_unavailability_map.get(resource.resourceCode):
                        intervals.append(model.NewFixedSizeIntervalVar(interval[0], interval[1] - interval[0],
                                                                       'unavailable_resource%i' % r))

                model.AddNoOverlap(intervals)

        # constraint: we verify that activity relations are respected
        for activity_relation in self.activity_relation_list:
            t1 = self.activity_index_by_activity_name.get(activity_relation.firstActivityCode)
            t2 = self.activity_index_by_activity_name.get(activity_relation.secondActivityCode)

            relation_type = activity_relation.relationType
            relation_var = []

            if relation_type == 'END_START':  # start[t2] - end[t1] must be >=relationWindowMin and <=relationWindowMax
                relation_var.append(start_activity[t2])
                relation_var.append(end_activity[t1])
            elif relation_type == 'END_END':  # end[t2] - end[t1] must be >=relationWindowMin and <=relationWindowMax
                relation_var.append(end_activity[t2])
                relation_var.append(end_activity[t1])
            elif relation_type == 'START_START':  # start[t2] - start[t1] must be >=relationWindowMin and <=relationWindowMax
                relation_var.append(start_activity[t2])
                relation_var.append(start_activity[t1])
            elif relation_type == 'START_END':  # end[t2] - start[t1]must be >=relationWindowMin and <=relationWindowMax
                relation_var.append(end_activity[t2])
                relation_var.append(start_activity[t1])

            coefficients = [1, -1]

            model.Add(
                cp_model.LinearExpr.WeightedSum(relation_var, coefficients) >= activity_relation.relationWindowMin)
            model.Add(
                cp_model.LinearExpr.WeightedSum(relation_var, coefficients) <= activity_relation.relationWindowMax)

        #setup
        #input setupMap dict key=resource_code value=matrix #activity*#activity
        for resource_set_name in self.resource_list_by_resource_set.keys():
            for resource in self.resource_list_by_resource_set[resource_set_name]:
                if resource.resourceCode in self.setupMap.keys():

                    r = self.resource_index_by_resource_name[resource.resourceCode]

                    setup_for_resource = self.setupMap[resource.resourceCode]
                    arcs = []

                    start_lit_00 = model.NewBoolVar(f'resource {r} not used')
                    arcs.append((0, 0, start_lit_00))

                    for j in range(self.n_activity):

                        if self.activity_resource_compatibility[j][r] == 1:

                            activity_j = self.activity_index_by_activity_name[self.activity_list[j].activityCode]

                            start_lit_1 = model.NewBoolVar(f'{activity_j} is first')
                            arcs.append((0, activity_j+1, start_lit_1))

                            start_lit_2 = model.NewBoolVar(f'{activity_j} is last')
                            arcs.append((activity_j+1, 0, start_lit_2))

                            arcs.append((activity_j+1, activity_j+1, assigned_activity_to_resource_of_resource_set[(activity_j, r, resource_set_name)].Not()))

                            for k in range(self.n_activity):
                                if k != j and self.activity_resource_compatibility[k][r] == 1:

                                    activity_k = self.activity_index_by_activity_name[self.activity_list[k].activityCode]

                                    lit = model.NewBoolVar(f'{activity_j} before {activity_k}')
                                    arcs.append((activity_j+1, activity_k+1, lit))

                                    model.Add(start_activity_to_resource_of_resource_set[(activity_k, r, resource_set_name)] >=
                                              end_activity_to_resource_of_resource_set[(activity_j, r, resource_set_name)] +
                                              int(setup_for_resource[j][k])).OnlyEnforceIf(lit)

                    # primo_nodo = np.zeros(len(arcs))
                    # secondo_nodo = np.zeros(len(arcs))
                    # link = np.zeros(len(arcs))
                    #
                    # for i, arc in enumerate(arcs):
                    #     primo_nodo[i] = arc[0]
                    #     secondo_nodo[i] = arc[1]
                    #     link[i] = arc[2]

                    model.AddCircuit(arcs)

        # objective : min makespan, min tardiness

        if self.param_map['OBJECTIVE'] == 'MIN_MAKESPAN':
            makespan = model.NewIntVar(0, self.T, 'makespan')
            model.AddMaxEquality(makespan, end_activity.values())
            model.Minimize(makespan)

        if self.param_map['OBJECTIVE'] == 'MIN_TARDINESS':
            tardiness = []
            for t in range(self.n_activity):
                tardiness[t] = model.NewIntVar(0, self.T, 'tardiness_activity%i' % t)
                model.Add(tardiness[t] == end_activity[t] - self.activity_due_time[t]).OnlyEnforceIf(
                    end_activity[t] - self.activity_due_time[t] > 0)
                model.Add(tardiness[t] == 0).OnlyEnforceIf(end_activity[t] - self.activity_due_time[t] <= 0)

            model.Minimize(tardiness)

        # solver
        solver = cp_model.CpSolver()
        solver_time = int(self.param_map['TIME_LIMIT'])
        solver.parameters.max_time_in_seconds = solver_time
        #solver.parameters.log_search_progress = True
        status = solver.Solve(model)  # 4 : optimal , 3 : infeasible, 2 : feasible
        time = solver.WallTime()

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            str_status = ''
            if status == 4:
                str_status = 'OPTIMAL'
            elif status == 2:
                str_status = 'FEASIBLE'
            print(f'Status {str_status} time {time}, solution: ')
            print(f'makespan {solver.Value(makespan)}')
            for activity in self.activity_list:
                a = self.activity_index_by_activity_name.get(activity.activityCode)
                for resourceSetName in activity.resourceSetList:
                    for resource in self.resource_list_by_resource_set[resourceSetName]:
                        r = self.resource_index_by_resource_name.get(resource.resourceCode)
                        if self.activity_resource_compatibility[a][r]:
                            if solver.Value(assigned_activity_to_resource_of_resource_set[(a, r, resourceSetName)]):
                                print(
                                    f'activity {activity.activityCode} start {solver.Value(start_activity_to_resource_of_resource_set[a, r, resourceSetName])} end '
                                    f'{solver.Value(end_activity_to_resource_of_resource_set[a, r, resourceSetName])}, resource {resource.resourceCode}, '
                                    f'of resource set {resourceSetName}')

        elif status == cp_model.INFEASIBLE:
            print('Not feasible solution found')
        else:
            print('bho')

    def build_plan(self):
        return
