import sys
from dataclasses import dataclass, field
from dataenv import *

@dataclass
class Converter:
    activity_list: list = field(default_factory=list)
    resource_list: list = field(default_factory=list)
    availability_map: dict = field(default_factory=dict)
    metric_list: list = field(default_factory=list)

    def __init__(self, problem):
        self.activity_list = problem._activities
        self.resource_list = problem.fluents
        self.availability_map = problem._base.effects
        self.metric_list = problem.quality_metrics

    def build_scheduling_problem(self):

        resource_list = []
        resource_index_by_name = {}
        avalilability_list_by_resource_code = {}
        resource_availability_map = {}
        resource_set_list = []
        resource_set_by_resource = {}
        resource_set_resource_list = []

        index = 0
        for resource in self.resource_list:
            if (resource.type.upper_bound > 1):
                resource_set_sp_name = resource.name
                for index in range(resource.type.upper_bound):
                    resource_code = resource.name + str(index)
                    resource_set_by_resource[resource_code] = resource_set_sp_name
                    resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                    resource_set_resource_list.append(resource_set_resource)
                    resource_sp = Resource(resource_code)
                    resource_list.append(resource_sp)
                    resource_index_by_name[resource_code] = index
                    ++index
            else:
                resource_code = resource.name
                resource_set_sp_name = resource.name
                resource_set_by_resource[resource_code] = resource_set_sp_name
                resource_set_resource = ResourceSetResource(resource_set_sp_name, resource_code)
                resource_set_resource_list.append(resource_set_resource)
                resource_sp = Resource(resource_code)
                resource_list.append(resource_sp)
                resource_index_by_name[resource_code] = index
                ++index


            resource_set_list.append(resource_set_sp_name)


        availability_resource_code_time_list = []
        for key in self.availability_map:
            for value in self.availability_map[key]:
                if value.kind.is_decrease():
                    availability_resource_code_time_list.append((str(value.fluent),'start',key.delay))
                elif value.kind.is_increase():
                    availability_resource_code_time_list.append((str(value.fluent),'end',key.delay))
        availability_list_by_resource_code = {}
        for resource in resource_list:
            filtered_list= [x for x in availability_resource_code_time_list if x[0] in resource.resourceCode]
            if filtered_list:
                filtered_list.sort(key = lambda x : x[2])
                temp = []
                for ii in range(len(filtered_list)-1):
                    if filtered_list[ii][1]!='start' and filtered_list[ii+1][1]!='end':
                        print('qualcosa non va')
                    else:
                        start = filtered_list[ii][2]
                        end = filtered_list[ii+1][2]
                        availability = ResourceAvailability(start, end, 'UNAVAILABLE')
                        temp.append(availability)
                avalilability_list_by_resource_code[resource.resourceCode] = temp

        for resource_code in avalilability_list_by_resource_code.keys():
            index = resource_index_by_name[resource_code]
            resource_list[index].resourceAvailabilityList.extend(availability_list_by_resource_code[resource_code])

        activity_index_by_name = {}
        activity_activity_relation_list = []
        activity_list = []
        seize_release_list = []

        for ii in range(len(self.activity_list)):
            activity_sp_name = self.activity_list[ii].name
            activity_sp_processing_time = int(str(self.activity_list[ii].duration.upper))
            activity_sp_due_time = 2147483647 # max long value in C
            activity_sp_release_time = 0

            for constraint in self.activity_list[ii]._constraints:

                if str(constraint.args[0]) == 'end(' + activity_sp_name + ')' and constraint.args[1].is_int_constant() \
                        and constraint.is_le():
                    activity_sp_due_time = constraint.args[1].int_constant_value()

                if constraint.args[0].is_int_constant() and str(constraint.args[1]) == 'start(' + activity_sp_name + ')' \
                        and constraint.is_le():
                    activity_sp_release_time = constraint.args[0].int_constant_value()

                if (str(constraint.args[0]) == 'start(' + activity_sp_name + ')' or str(
                        constraint.args[0]) == 'end(' + activity_sp_name + ')') and \
                        ('end' in str(constraint.args[1]) or 'start' in str(
                            constraint.args[1])) and constraint.constraint.is_le():
                    first_code = str(constraint.args[0]).split('(')[1].replace(')', '')
                    second_code = str(constraint.args[1]).split('(')[1].replace(')', '')
                    relation = str(constraint.args[0]).split('(')[0].upper() + '_' + str(constraint.args[1]).split('(')[
                        0].upper()
                    act_act_relation = ActivityActivityRelation(first_code, second_code, relation)
                    activity_activity_relation_list.append(act_act_relation)

            activity_sp = Activity(activity_sp_name, activity_sp_processing_time, activity_sp_release_time,
                                   activity_sp_due_time)

            activity_list.append(activity_sp)
            activity_index_by_name[activity_sp_name] = ii

            for key in self.activity_list[ii].effects.keys():
                if key == self.activity_list[ii].start:
                    activity_code = str(key).split('(')[1].replace(')', '')
                    for effect in self.activity_list[ii].effects[key]:
                        resource_set_code = str(effect.fluent)
                        for j in range(effect.value.int_constant_value()):
                            sr_name = 'seize_release_' + activity_code + '#' + str(j)
                            seize_release = ResourceSetActivitySeizeRelease(sr_name, resource_set_code, activity_code,
                                                                            activity_code)
                            seize_release_list.append(seize_release)

        parameter_list = []

        for metric in self.metric_list:
            if str(metric)=='minimize makespan':
                objective = Parameter('OBJECTIVE', 'MIN_MAKESPAN')
                parameter_list.append(objective)


        ##manca caso tardiness, horizon e time limit

        scheduling_problem = Scheduling_problem(parameter_list, [], seize_release_list, resource_set_resource_list,
                                                resource_set_list, resource_list, activity_activity_relation_list, activity_list, [])

        return scheduling_problem


    def build_up_plan(self):
        ####
        return plan











