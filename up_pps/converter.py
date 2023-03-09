import sys
from dataclasses import dataclass, field

import up_pps
from up_pps import *
from unified_planning.model.scheduling.schedule import Schedule
import unified_planning as up


@dataclass
class Converter:
    activity_list: list = field(default_factory=list)
    activity_map: dict = field(default_factory=dict)
    resource_list: list = field(default_factory=list)
    object_list: list = field(default_factory=list)
    availability_map: dict = field(default_factory=dict)
    metric_list: list = field(default_factory=list)
    constraint_list: list = field(default_factory=list)
    initial_values_map: dict = field(default_factory=dict)
    original_resource_set_of_resource_set: dict = field(default_factory=dict)

    def __init__(self, problem):
        self.activity_list = problem._activities
        self.activity_map = {a.name: a for a in self.activity_list}
        self.resource_list = problem.fluents
        self.object_list = problem._objects
        self.object_map = {o.name: o for o in self.object_list}
        self.availability_map = problem._base.effects
        self.metric_list = problem.quality_metrics
        self.constraint_list = problem.constraints
        self.initial_values_map = problem.explicit_initial_values
        self.original_resource_set_of_resource_set = {}

    def build_scheduling_problem(self):

        resource_list = []
        resource_index_by_name = {}
        resource_set_list = []
        resource_set_by_resource = {}
        resource_set_resource_list = []

        index_res = 0

        for resource in self.resource_list:
            if resource.type.is_int_type():
                if len(resource.signature) > 0:
                    resource_set_sp_name = resource.name
                    for obj in self.object_list:
                        if obj.type == resource.signature[0].type:
                            resource_code = obj.name
                            resource_set_by_resource[resource_code] = resource_set_sp_name
                            resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                            resource_set_resource_list.append(resource_set_resource)
                            resource_sp = Resource(resource_code)
                            resource_list.append(resource_sp)
                            resource_index_by_name[resource_code] = index_res
                            index_res += 1
                elif resource.type.upper_bound > 1:
                    resource_set_sp_name = resource.name
                    for index in range(resource.type.upper_bound):
                        resource_code = resource.name + str(index)
                        resource_set_by_resource[resource_code] = resource_set_sp_name
                        resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                        resource_set_resource_list.append(resource_set_resource)
                        resource_sp = Resource(resource_code)
                        resource_list.append(resource_sp)
                        resource_index_by_name[resource_code] = index_res
                        index_res += 1
                else:
                    resource_code = resource.name
                    resource_set_sp_name = resource.name
                    resource_set_by_resource[resource_code] = resource_set_sp_name
                    resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                    resource_set_resource_list.append(resource_set_resource)
                    resource_sp = Resource(resource_code)
                    resource_list.append(resource_sp)
                    resource_index_by_name[resource_code] = index_res
                    index_res += 1
                # else: # ha senso considerare una risorsa di tipo bool?
                #     resource_code = resource.name
                #     resource_set_sp_name = resource.name
                #     resource_set_by_resource[resource_code] = resource_set_sp_name
                #     resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                #     resource_set_resource_list.append(resource_set_resource)
                #     resource_sp = Resource(resource_code)
                #     resource_list.append(resource_sp)
                #     resource_index_by_name[resource_code] = index_res
                #     index_res += 1

                resource_set_list.append(resource_set_sp_name)

        availability_resource_code_time_list = []
        for key in self.availability_map:
            for value in self.availability_map[key]:
                resource_code_av = str(value.fluent) if "rset_" not in str(value.fluent) else \
                    str(value.fluent).split("(")[1].replace(")", "")
                if value.kind.name == "DECREASE":
                    availability_resource_code_time_list.append((resource_code_av, 'start', key.delay))
                elif value.kind.name == "INCREASE":
                    availability_resource_code_time_list.append((resource_code_av, 'end', key.delay))
        availability_list_by_resource_code = {}
        for resource in resource_list:
            filtered_list = [x for x in availability_resource_code_time_list if x[0] in resource.resourceCode]
            if filtered_list:
                filtered_list.sort(key=lambda x: x[2])
                temp = []
                for ii in range(0, len(filtered_list) - 1, 2):
                    if filtered_list[ii][1] != 'start' and filtered_list[ii + 1][1] != 'end':
                        print('qualcosa non va')
                    else:
                        start = filtered_list[ii][2]
                        end = filtered_list[ii + 1][2]
                        availability = ResourceAvailability(start, end, 'UNAVAILABLE')
                        temp.append(availability)
                availability_list_by_resource_code[resource.resourceCode] = temp

        for resource_code in availability_list_by_resource_code.keys():
            if resource_code in availability_list_by_resource_code.keys():
                index = resource_index_by_name[resource_code]
                resource_list[index].resourceAvailabilityList.extend(availability_list_by_resource_code[resource_code])

        activity_index_by_name = {}
        activity_activity_relation_list = []
        activity_list = []
        seize_release_list = []

        pbm_resource_map = {r.name: r for r in self.resource_list}
        resource_map = {r.resourceCode: r for r in resource_list}

        def obtain_map(c):
            if 'end' in str(c[0].args[0]) or 'start' in str(c[0].args[0]):
                return str(c[0].args[0]).split('(')[1].replace(')', '')
            elif c[0].args[0].is_int_constant():
                return str(c[0].args[1]).split('(')[1].replace(')', '')
            elif str(c[0]).split('(')[0] in pbm_resource_map.keys() and pbm_resource_map.get(
                    str(c[0]).split('(')[0]).type.is_bool_type() \
                    and pbm_resource_map.get(str(c[0]).split('(')[0]).signature[0].name == str(c[0]).split(':')[
                1].replace(')', ''):
                return str(c[0]).split('(')[1].split(':')[0]

        constraint_by_activity_map = {}

        for c in self.constraint_list:
            key = obtain_map(c)
            if key not in constraint_by_activity_map:
                constraint_by_activity_map[key] = []
            constraint_by_activity_map[key].append(c[0])

        initial_value_map = {list(k.get_contained_names())[0] + '(' + list(k.get_contained_names())[1] + ')': \
                                 v.bool_constant_value() for (k, v) in list(self.initial_values_map.items())}
        resource_set_for_param = {}

        for ii, act in enumerate(self.activity_list):
            activity_sp_name = act.name
            activity_sp_processing_time = int(str(act.duration.upper))
            activity_sp_due_time = 2147483647  # max long value in C
            activity_sp_release_time = 0

            for constraint in constraint_by_activity_map.get(activity_sp_name):

                if str(constraint.args[0]) == 'end(' + activity_sp_name + ')' and constraint.args[1].is_int_constant() \
                        and constraint.is_le():
                    activity_sp_due_time = constraint.args[1].int_constant_value()

                elif constraint.args[0].is_int_constant() and str(
                        constraint.args[1]) == 'start(' + activity_sp_name + ')' \
                        and constraint.is_le():
                    activity_sp_release_time = constraint.args[0].int_constant_value()

                elif ('end' in str(constraint.args[0]) or 'start' in str(constraint.args[0])) and (
                        'end' in str(constraint.args[1]) or 'start' in str(constraint.args[1])) \
                        and (constraint.is_le() or constraint.is_lt()):
                    first_code = str(constraint.args[0]).split('(')[1].replace(')', '')
                    second_code = str(constraint.args[1]).split('(')[1].replace(')', '')
                    relation = str(constraint.args[0]).split('(')[0].upper() + '_' + \
                               str(constraint.args[1]).split('(')[
                                   0].upper()
                    act_act_relation = ActivityActivityRelation(first_code, second_code, relation)
                    activity_activity_relation_list.append(act_act_relation)

                elif str(constraint).split('(')[0] in pbm_resource_map.keys() and pbm_resource_map.get(
                        str(constraint).split('(')[0]).type.is_bool_type() \
                        and pbm_resource_map.get(str(constraint).split('(')[0]).signature[0].name == \
                        str(constraint).split(':')[1].replace(')', ''):

                    new_resource_set_name = str(constraint).split('(')[0]
                    resource_set_list.append(new_resource_set_name)

                    for obj in self.object_list:
                        if obj.type == pbm_resource_map.get(str(constraint).split('(')[0]).signature[0].type:
                            key_name = str(constraint).split('(')[0] + '(' + obj.name + ')'
                            if initial_value_map.get(key_name):
                                resource_to_add = resource_map.get(obj.name)
                                # resource_set_by_resource[resource_to_add.resourceCode] = new_resource_set_name
                                resource_set_resource = ResourceSetResource(new_resource_set_name,
                                                                            resource_to_add.resourceCode)
                                resource_set_resource_list.append(resource_set_resource)
                                param_name = str(constraint).split('(')[1].replace(')', '')
                                resource_set_for_param[param_name] = new_resource_set_name

            activity_sp = Activity(activity_sp_name, activity_sp_processing_time, activity_sp_release_time,
                                   activity_sp_due_time)

            activity_list.append(activity_sp)
            activity_index_by_name[activity_sp_name] = ii

            for key in self.activity_list[ii].effects.keys():
                if key.timepoint == self.activity_list[ii].start:
                    activity_code = str(key).split('(')[1].replace(')', '')
                    for effect in self.activity_list[ii].effects[key]:
                        resource_set_code = None
                        if "(" in str(effect.fluent):
                            param_name = str(effect.fluent).split("(")[1].replace(")", "")
                            if param_name in resource_set_for_param.keys():
                                resource_set_code = resource_set_for_param.get(param_name)
                                self.original_resource_set_of_resource_set[str(effect.fluent).split("(")[0]] = \
                                resource_set_for_param.get(param_name)
                            else:
                                print("Undefined parameter " + param_name)
                        else:
                            resource_set_code = str(effect.fluent)
                        for j in range(effect.value.int_constant_value()):
                            sr_name = 'seize_release_' + activity_code + '_' + resource_set_code + '#' + str(j)
                            seize_release = ResourceSetActivitySeizeRelease(sr_name, resource_set_code, activity_code,
                                                                            activity_code)
                            seize_release_list.append(seize_release)

        parameter_list = []

        for metric in self.metric_list:
            if str(metric) == 'minimize makespan':
                objective = Parameter('OBJECTIVE', 'MIN_MAKESPAN')
                parameter_list.append(objective)

        ##manca caso tardiness

        scheduling_problem = Scheduling_problem(parameter_list, [], seize_release_list, resource_set_resource_list,
                                                resource_set_list, resource_list, activity_activity_relation_list,
                                                activity_list, [])

        return scheduling_problem


    def build_up_plan(self, solution: up_pps.core.output.cp_solution_output) -> 'unified_planning.model.scheduling.schedule':
        assignment_dict = {}
        activities_list = []
        for sol in solution.solution_output_list:
            act = self.activity_map[sol.activity_name]
            assignment_dict[act.start] = sol.activity_start
            assignment_dict[act.end] = sol.activity_end
            activities_list.append(act)
            if len(act.parameters) > 0:
                list_resource_set = [str(x.fluent) for x in list(act.effects.values())[0]]
                for param in act.parameters:
                    param_name = param.name
                    for res_set in list_resource_set:
                        if param_name in res_set:
                            resource_set_original = res_set.split('(')[0]
                            new_resource_set = self.original_resource_set_of_resource_set[resource_set_original]
                            resource_name = sol.resource_name_by_resource_set_name[new_resource_set]
                            for res in resource_name:
                                obj = self.object_map.get(res)
                                assignment_dict[param] = obj

        up_plan = Schedule(assignment=assignment_dict, activities=activities_list)
        return up_plan
