from networkx import *
import networkx as nx


class GraphActivity:

    def __init__(self):
        self.graph_activity = nx.DiGraph()

    def build_graph_activity(self, activity_list, activity_activity_relation_list):

        for activity in activity_list:
            self.graph_activity.add_node(activity.activityCode+'_start')
            self.graph_activity.add_node(activity.activityCode+'_end')
            self.graph_activity.add_edge(activity.activityCode+'_start', activity.activityCode+'_end')

        for activity_relation in activity_activity_relation_list:
            relation = activity_relation.relationType.split('_')
            v1 = activity_relation.firstActivityCode+'_'+relation[0].lower()
            v2 = activity_relation.secondActivityCode+'_'+relation[1].lower()
            self.graph_activity.add_edge(v1, v2)

    def set_resource_set_to_activity_fact(self, activity_fact_list, activity_index_by_name, seize_release_list):

        for seize_release in seize_release_list:
            v1 = seize_release.seizeReleaseSeizingActivityCode+'_start'
            v2 = seize_release.seizeReleaseReleasingActivityCode+'_end'
            path = nx.shortest_path(self.graph_activity, v1, v2)

            for ii in range(len(path)):
                if '_start' in path[ii]:
                    path[ii] = path[ii].replace('_start', '')
                elif '_end' in path[ii]:
                    path[ii] = path[ii].replace('_end', '')
            path = list(dict.fromkeys(path))

            for activity_code in path:
                index = activity_index_by_name.get(activity_code)
                activity_fact_list[index].add_resource_set_to_list(seize_release.seizeReleaseResourceSetName)
                activity_fact_list[index].add_seize_release_resource_set_to_map(seize_release.seizeReleaseName, seize_release.seizeReleaseResourceSetName)




