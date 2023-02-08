from up_pps.manager.activity_fact_manager import ActivityFactManager
from dataclasses import dataclass, field
import numpy as np


@dataclass
class InstanceManager:
    parameter_map: dict = field(default_factory=dict)
    resource_list: list = field(default_factory=list)
    resource_list_by_resource_set: dict = field(default_factory=dict)
    resource_map: dict = field(default_factory=dict)
    activity_fact_list: list = field(default_factory=list)
    activity_fact_map: dict = field(default_factory=dict)
    activity_relation_list: list = field(default_factory=list)
    seize_release_list: list = field(default_factory=list)
    seize_release_activity_map: dict = field(default_factory=dict)
    setup_time_map: dict = field(default_factory=dict)

    def build_instance_manager(self, scheduling_problem):

        for resource in scheduling_problem.resourceList:
            self.resource_map[resource.resourceCode] = resource
            self.resource_list.append(resource)

        for resource_set_resource in scheduling_problem.resourceSetResourceList:
            if not resource_set_resource.resourceSetName in self.resource_list_by_resource_set.keys():
                self.resource_list_by_resource_set[resource_set_resource.resourceSetName] = []
            self.resource_list_by_resource_set[resource_set_resource.resourceSetName].append(
                self.resource_map[resource_set_resource.resourceCode])

        activity_fact_manager = ActivityFactManager()
        activity_fact_manager.build_manager(scheduling_problem.activityList,
                                            scheduling_problem.activityActivityRelationList,
                                            scheduling_problem.resourceSetActivitySeizeReleaseList)

        self.activity_fact_list = activity_fact_manager.activity_fact_list
        activity_fact_code_list = [x.activityCode for x in self.activity_fact_list]
        self.activity_fact_map = activity_fact_manager.activity_fact_map
        self.activity_relation_list = scheduling_problem.activityActivityRelationList
        self.seize_release_list = scheduling_problem.resourceSetActivitySeizeReleaseList

        for parameter in scheduling_problem.parameterList:
            self.parameter_map[parameter.parameterName] = parameter.parameterValue

        # we create a dict with key : seize release name value: set of activities linked to the seize_release
        for activity in self.activity_fact_list:
            for seize_release in activity.seizeReleaseAndResourceSet.keys():
                if seize_release not in self.seize_release_activity_map.keys():
                    self.seize_release_activity_map[seize_release] = set()
                self.seize_release_activity_map[seize_release].add(activity)

        # self.checkMultipleSeizeRelease()

        # create setupMap
        n_activity = len(self.activity_fact_list)
        for setup in scheduling_problem.setupTimeList:
            if not setup.resourceCode in self.setup_time_map.keys():
                self.setup_time_map[setup.resourceCode] = np.zeros((n_activity, n_activity))

            activity_0 = activity_fact_code_list.index(setup.firstActivityCode)
            activity_1 = activity_fact_code_list.index(setup.secondActivityCode)

            self.setup_time_map[setup.resourceCode][activity_0][activity_1] = setup.setupTime

        self.checkHorizon()


    # we check if there exist activities that has multiple seize release associated to the same resource set.
    # If there are, we change the resource set name ad update everything
    def checkMultipleSeizeRelease(self):

        for activity in self.activity_fact_list:
            for resource_set_name in set(activity.resourceSetList):
                times_resource_set_repeated = activity.resourceSetList.count(resource_set_name)
                if times_resource_set_repeated > 1:  # if a resource set is called more than once by the activity
                    original_resource_set_name = resource_set_name
                    # we change the resource set name of the resource set repeated, excluded the first one
                    indexes = np.where(np.array(activity.resourceSetList) == original_resource_set_name)[0]
                    for i, value in enumerate(indexes[1:]):
                        activity.resourceSetList[value] = original_resource_set_name + '_' + str(i + 1)
                    # identically, we change the resource set name associated with the seize release name and update the
                    # resource set name of the seize release object associated
                    indexes = [k for k, v in activity.seizeReleaseAndResourceSet.items() if
                               v == original_resource_set_name]
                    for i, value in enumerate(indexes[1:]):
                        activity.seizeReleaseAndResourceSet[value] = original_resource_set_name + '_' + str(i + 1)
                        ii = [x.seizeReleaseName for x in self.seize_release_list].index(value)
                        self.seize_release_list[
                            ii].seizeReleaseResourceSetName = original_resource_set_name + '_' + str(i + 1)

                    # we now add in the dict resource_list_by_resource_set the new resource set names giving as value
                    # the list of resources associated with the original resource set name
                    list_of_resource_of_original_resource_set = self.resource_list_by_resource_set[
                        original_resource_set_name]

                    for ii in range(times_resource_set_repeated - 1):
                        if original_resource_set_name + '_' + str(
                                ii + 1) not in self.resource_list_by_resource_set.keys():
                            self.resource_list_by_resource_set[original_resource_set_name + '_' + str(
                                ii + 1)] = list_of_resource_of_original_resource_set


    def checkHorizon(self):

        if not 'HORIZON' in self.parameter_map.keys():
            max_processing_time = max([x.activityProcessingTime for x in self.activity_fact_list])
            horizon = max_processing_time * len(self.activity_fact_list)
            self.parameter_map['HORIZON'] = str(horizon)
