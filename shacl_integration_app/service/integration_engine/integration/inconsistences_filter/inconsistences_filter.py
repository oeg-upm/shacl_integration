from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster
from shacl_integration_app.repository.rule_library.filter_library import Filter_Library
from rdflib import Graph

class InconsistencesFilter:
    """
    Class to filter inconsistencies in the SHACL integration process.
    """
    def __init__(self, concept_clusters: list[Cluster], inconsistences_report_path: str) -> None:
        self.concept_clusters: list[Cluster] = concept_clusters
        self.final_clusters: list[Cluster] = []
        self.inconsistences_report_path: str = ''
        self.inconsistences_graph: Graph = Graph()
        self.inconsistences_filters_list: list[str] = [
            'http://www.w3.org/ns/shacl#nodeKind',
            'http://www.w3.org/ns/shacl#closed',
            'http://www.w3.org/ns/shacl#disjoint',
            'http://www.w3.org/ns/shacl#equals',
            'http://www.w3.org/ns/shacl#or',
            'http://www.w3.org/ns/shacl#and',
            'http://www.w3.org/ns/shacl#xone',
            'http://www.w3.org/ns/shacl#not',
            'http://www.w3.org/ns/shacl#uniqueLang',
            'http://www.w3.org/ns/shacl#languageIn',
            'http://www.w3.org/ns/shacl#in',
            'http://www.w3.org/ns/shacl#minCount',
            'http://www.w3.org/ns/shacl#maxCount',
            'http://www.w3.org/ns/shacl#minExclusive',
            'http://www.w3.org/ns/shacl#maxExclusive',
            'http://www.w3.org/ns/shacl#minInclusive',
            'http://www.w3.org/ns/shacl#maxInclusive',
            'http://www.w3.org/ns/shacl#minLength',
            'http://www.w3.org/ns/shacl#maxLength',
            'http://www.w3.org/ns/shacl#qualifiedMinCount',
            'http://www.w3.org/ns/shacl#qualifiedMaxCount',
        ]

    def filter_inconsistencies(self) -> list[Cluster]:
        """
        Filter inconsistencies from the SHACL data.
        """

        for cluster in self.concept_clusters:
            #print(f'Cluster: {cluster}')
            node_result: list[bool] = self.filter_node_inconsistences(list_node=cluster.node_axiom_cluster_list, cluster_concept=cluster.concept_list)
            property_result: list[bool] = [self.filter_property_inconsistences(prop=prop, cluster_concept=cluster.concept_list) for prop in cluster.property_cluster_list]
            if True not in node_result and True not in property_result:
                self.final_clusters.append(cluster)

        return self.final_clusters
    
    def filter_node_inconsistences(self, list_node: list[NodeAxiomCluster], cluster_concept: list[str]) -> bool:
        """
        Filter inconsistencies from the node axioms.
        """
        list_inconsistencies: list[bool] = []
        inconsistency: bool = False

        # print(f'Node: {list_node}')
        # print('\n')

        filter_dict: list[dict] = [
            {
                'filter' : ['http://www.w3.org/ns/shacl#nodeKind'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#closed'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#not'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#or'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#and'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#xone'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#equals', 'http://www.w3.org/ns/shacl#disjoint'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minCount', 'http://www.w3.org/ns/shacl#maxCount'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minExclusive', 'http://www.w3.org/ns/shacl#maxExclusive', 'http://www.w3.org/ns/shacl#minInclusive', 'http://www.w3.org/ns/shacl#maxInclusive'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minLength', 'http://www.w3.org/ns/shacl#maxLength'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#qualifiedMinCount', 'http://www.w3.org/ns/shacl#qualifiedMaxCount'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#uniqueLang', 'http://www.w3.org/ns/shacl#languageIn'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#in'],
                'list' : []
            }

        ]
        for node in list_node:
            [filter_dict[filter_dict.index(fil)]['list'].append(node) for fil in filter_dict if node.concept in fil['filter']]
        
        list_inconsistencies = [self.execute_filter(filter_dict=fil, cluster_concept=cluster_concept) for fil in filter_dict]

        list_inconsistencies = [False]
          
        return list_inconsistencies
        
    
    def filter_property_inconsistences(self, prop: PropertyCluster, cluster_concept: list[str]) -> bool:
        """
        Filter inconsistencies from the property axioms.
        ::return: False if there is no inconsistency, True if there is an inconsistency.
        """

        inconsistency: bool = False

        if not inconsistency:
            return False
        else:
            return True
        
    def execute_filter(self, filter_dict: dict[str|list[str]], cluster_concept: list[str]) -> bool:
        """
        Filter the inconsistencies from the SHACL data.
        """
        filter_result: list[bool] = []
        
        return filter_result
        
    def generate_inconsistences_report(self, cluster_concept: list[str], axiom: list[str]) -> str:
        """
        Generate the SHACL inconsistencies report.
        """
        # PREFIXES
        self.inconsistences_graph.bind('sh', 'http://www.w3.org/ns/shacl#')


        # self.inconsistences_graph.serialize(destination=self.inconsistences_report_path, format='turtle')
        return self.inconsistences_report_path