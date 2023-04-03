from up_pps.dataenv.internal.activity_fact import ActivityFact
from up_pps.dataenv.internal.graph import GraphActivity
from dataclasses import dataclass, field


@dataclass
class ActivityFactManager:
    activity_fact_list: list = field(default_factory=list)
    activity_fact_map: dict = field(default_factory=dict)

    def build_manager(self, activity_list, activity_activity_relation_list,
                      resource_set_activity_seize_release_list):

        activity_index_by_name = {}

        for ii in range(len(activity_list)):
            activity_fact = ActivityFact(activity_list[ii].activityCode,
                                         activity_list[ii].activityPriority,
                                         activity_list[ii].activityProcessingTime,
                                         activity_list[ii].activityReleaseTime,
                                         activity_list[ii].activityDueTime)
            self.activity_fact_list.append(activity_fact)
            activity_index_by_name[activity_fact.activityCode] = ii

        graph = GraphActivity()
        graph.build_graph_activity(activity_list, activity_activity_relation_list)

        graph.set_resource_set_to_activity_fact(self.activity_fact_list, activity_index_by_name,
                                                resource_set_activity_seize_release_list)

        for ii in range(len(self.activity_fact_list)):
            self.activity_fact_map[self.activity_fact_list[ii].activityCode] = self.activity_fact_list[ii]
