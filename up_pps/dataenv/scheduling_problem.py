from typing import Any
from dataclasses import dataclass, field
from up_pps import *
from up_pps.manager.instance_manager import InstanceManager
from up_pps.core.cp_solver import CpModel


@dataclass
class Scheduling_problem:
    parameterList: list = field(default_factory=list)
    elementList: list = field(default_factory=list)
    resourceSetActivitySeizeReleaseList: list = field(default_factory=list)
    resourceSetResourceList: list = field(default_factory=list)
    resourceSetList: list = field(default_factory=list)
    resourceList: list = field(default_factory=list)
    activityActivityRelationList: list = field(default_factory=list)
    activityList: list = field(default_factory=list)
    setupTimeList: list = field(default_factory=list)

    @staticmethod
    def from_json(obj: Any) -> 'Scheduling_problem':
        _parameter = [Parameter.from_dict(y) for y in obj.get("parameterList")]
        _element = [Element.from_dict(y) for y in obj.get("elementList")]
        _resourceSetActivitySeizeRelease = [ResourceSetActivitySeizeRelease.from_dict(y) for y in
                                            obj.get("resourceSetActivitySeizeReleaseList")]
        _resourceSetResource = [ResourceSetResource.from_dict(y) for y in obj.get("resourceSetResourceList")]
        _resourceSet = [ResourceSet.from_dict(y) for y in obj.get("resourceSetList")]
        _resource = [Resource.from_dict(y) for y in obj.get("resourceList")]
        _activityActivityRelation = [ActivityActivityRelation.from_dict(y) for y in
                                     obj.get("activityActivityRelationList")]
        _activity = [Activity.from_dict(y) for y in obj.get("activityList")]
        return Scheduling_problem(_parameter, _element, _resourceSetActivitySeizeRelease, _resourceSetResource,
                                  _resourceSet, _resource, _activityActivityRelation, _activity)

    def add_parameter(self, parameter):
        self.parameterList.append(parameter)

    def add_element(self, element):
        self.elementList.append(element)

    def add_resource_set_activity_seize_release(self, resource_set_activity_seize_release):
        self.resourceSetActivitySeizeReleaseList.append(resource_set_activity_seize_release)

    def add_resource_set(self, resource_set):
        self.resourceSetList.append(resource_set)

    def add_resource_set_resource(self, resource_set_resource):
        self.resourceSetResourceList.append(resource_set_resource)

    def add_resource(self, resource):
        self.resourceList.append(resource)

    def add_activity(self, activity):
        self.activityList.append(activity)

    def add_activity_activity_relation(self, activity_activity_relation):
        self.activityActivityRelationList.append(activity_activity_relation)

    def add_setup_time(self, setup):
        self.setupTimeList.append(setup)

    def add_setup_time_list(self, setup):
        self.setupTimeList.extend(setup)

    def add_parameter_list(self, parameter):
        self.parameterList.extend(parameter)

    def add_element_list(self, element):
        self.elementList.extend(element)

    def add_resource_set_activity_seize_release_list(self, resource_set_activity_seize_release):
        self.resourceSetActivitySeizeReleaseList.extend(resource_set_activity_seize_release)

    def add_resource_set_list(self, resource_set):
        self.resourceList.extend(resource_set)

    def add_resource_set_resource_list(self, resource_set_resource):
        self.resourceSetResourceList.extend(resource_set_resource)

    def add_resource_list(self, resource):
        self.resourceList.extend(resource)

    def add_activity_list(self, activity):
        self.activityList.extend(activity)

    def add_activity_activity_relation_list(self, activity_activity_relation):
        self.activityActivityRelationList.extend(activity_activity_relation)

    def print(self):
        print("INSTANCE")
        print()
        if self.activityList:
            print("Activity:\n", end='\t')
            print(*self.activityList, sep='\n\t')
            print()
        if self.activityActivityRelationList:
            print("Activity_Activity_Relation:\n", end='\t')
            print(*self.activityActivityRelationList, sep='\n\t')
            print()
        if self.elementList:
            print("Element:\n", end='\t')
            print(*self.elementList, sep='\n\t')
            print()
        if self.resourceList:
            print("Resource:\n", end='\t')
            print(*self.resourceList, sep='\n\t')
            print()
        if self.resourceSetList:
            print("Resource_Set:\n", end='\t')
            print(*self.resourceSetList, sep='\n\t')
            print()
        if self.resourceSetResourceList:
            print("Resource_Set_Resource:\n", end='\t')
            print(*self.resourceSetResourceList, sep='\n\t')
            print()
        if self.resourceSetActivitySeizeReleaseList:
            print("Resource_Set_Activity_Seize_Release:\n", end='\t')
            print(*self.resourceSetActivitySeizeReleaseList, sep='\n\t')
            print()
        if self.parameterList:
            print("Parameter:\n", end='\t')
            print(*self.parameterList, sep='\n\t')
            print()

