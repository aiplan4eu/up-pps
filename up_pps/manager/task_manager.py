from typing import List
from typing import Any
from dataclasses import dataclass


class Task:

    # def __init__(self):
    #     self.taskName = None
    #     self.releaseTime = None
    #     self.dueTime = None
    #     self.priority = None
    #     self.processingTime = None
    #     self.resourceSetName = None
    #     self.seizingActivityCode = None
    #     self.releasingActivityCode = None

    def __init__(self, taskName, releaseTime, dueTime, priority, processingTime, resourceSetName, seizingActivityCode,
                 releasingActivityCode):
        self.taskName = taskName
        self.releaseTime = int(releaseTime)
        self.dueTime = int(dueTime)
        self.priority = int(priority)
        self.processingTime = int(processingTime)
        self.resourceSetName = resourceSetName
        self.seizingActivityCode = seizingActivityCode
        self.releasingActivityCode = releasingActivityCode

    def build_task(self):
        pass


class TaskRelation:

    # def __init__(self):
    #     self.firstTaskName = None
    #     self.secondTaskName = None
    #     self.relationType = None
    #     self.windowMax = None
    #     self.windowMin = None
    def __init__(self, firstTaskName, secondTaskName, relationType, windowMax, windowMin):
        self.firstTaskName = firstTaskName
        self.secondTaskName = secondTaskName
        self.relationType = relationType
        self.windowMax = windowMax
        self.windowMin = windowMin

    def build_task_relation(self):
        pass


@dataclass
class TaskManager:

    # def __init__(self):
    #     self.taskMap = None
    #     self.taskList = None
    #     self.taskRelationList = None
    #     self.taskNameListByActivityCode = None

    def __init__(self, taskList, taskRelationList):
        self.taskMap = {}
        self.taskList = taskList
        self.taskRelationList = taskRelationList
        self.taskNameListByActivityCode = {}

    def build_task_manager(self):
        for task in self.taskList:
            self.taskMap[task.taskName] = task
