from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster
from rdflib import Graph, URIRef, RDF, Literal
from shacl_integration_app.repository.rule_library import *
import shacl_integration_app.service.rule_engine as rule_engine
rule_library: Rule_Library = Rule_Library()

class IntegrationOperation:
    """
    Class representing an integration operation.
    """

    def __init__(self, concept_clusters: list[Cluster], integration_option: str):
        """
        Initialize the IntegrationOperation instance.
        """
        self.concept_clusters: list[Cluster] = concept_clusters
        self.integration_option: str = integration_option
        self.integrated_shacl_shape: Graph = Graph()
        self.integrated_shape_path: str = ''

    def execute_integration(self) -> list[Cluster]:
        """
        Execute the integration operation.
        """
        new_cluster_list: list[Cluster] = []

        for cluster in self.concept_clusters:
            new_node_clusters: list[NodeAxiomCluster] = self.execute_node_integration(node_list=cluster.node_axiom_cluster_list)
            new_property_clusters: list[PropertyCluster] = [self.execute_property_integration(property=prop) for prop in cluster.property_cluster_list]

            cluster.node_axiom_cluster_list = new_node_clusters
            cluster.property_cluster_list = new_property_clusters
            new_cluster_list.append(cluster)

        return new_cluster_list
    

    
    def execute_node_integration(self, node_list: list[NodeAxiomCluster]) -> list[NodeAxiomCluster]:

        new_node_list: list[NodeAxiomCluster] = []
        for node in node_list:
            if node.concept == 'http://www.w3.org/ns/shacl#nodeKind':
                object_list: list = []
                if node.axiom_list != []:
                    for axiom in node.axiom_list:
                        logical_operator: str = None
                        if axiom['logical_operator'] != None:
                            logical_operator = axiom['logical_operator']
                        object_list.append(axiom['obj'])             
                    res = self.execute_nodekind_integration(nodekind_list=object_list)
                    node.axiom_list = [{
                        'logical_operator': logical_operator,
                        'obj': res
                    }]
            new_node_list.append(node)

        return new_node_list
    

    
    def execute_property_integration(self, property: PropertyCluster) -> PropertyCluster:
        print(f"Property: {property}")
        return
    
    def execute_nodekind_integration(self, nodekind_list: list) -> list[str]:
        nodeKindDict : dict = {
            "[1, 0, 0, 1, 0, 0]_union" : 'http://www.w3.org/ns/shacl#IRI',
            "[1, 0, 0, 1, 0, 0]_intersection" : 'http://www.w3.org/ns/shacl#IRI',
            "[0, 1, 0, 0, 1, 0]_union" : 'http://www.w3.org/ns/shacl#Literal',
            "[0, 1, 0, 0, 1, 0]_intersection" : 'http://www.w3.org/ns/shacl#Literal',
            "[0, 0, 1, 0, 0, 1]_union" : 'http://www.w3.org/ns/shacl#BlankNode',
            "[0, 0, 1, 0, 0, 1]_intersection" : 'http://www.w3.org/ns/shacl#BlankNode',
            "[1, 0, 0, 1, 1, 0]_union" : 'http://www.w3.org/ns/shacl#IRIOrLiteral',
            "[1, 0, 0, 1, 1, 0]_intersection" : 'http://www.w3.org/ns/shacl#IRI',
            "[0, 1, 0, 1, 1, 0]_union" : 'http://www.w3.org/ns/shacl#IRIOrLiteral',
            "[0, 1, 0, 1, 1, 0]_intersection" : 'http://www.w3.org/ns/shacl#Literal',
            "[1, 0, 0, 1, 0, 1]_union" : 'http://www.w3.org/ns/shacl#BlankNodeOrIRI',
            "[1, 0, 0, 1, 0, 1]_intersection" : 'http://www.w3.org/ns/shacl#IRI',
            "[0, 0, 1, 1, 0, 1]_union" : 'http://www.w3.org/ns/shacl#BlankNodeOrIRI',
            "[0, 0, 1, 1, 0, 1]_intersection" : 'http://www.w3.org/ns/shacl#BlankNode',
            "[0, 1, 0, 0, 1, 1]_union" : 'http://www.w3.org/ns/shacl#BlankNodeOrLiteral',
            "[0, 1, 0, 0, 1, 1]_intersection" : 'http://www.w3.org/ns/shacl#Literal'
        }
        fact = rule_engine.Fact(list=nodekind_list)

        res = rule_library.rule_multiple.evaluate_multiple_rules_with_result([fact], rule_library.integrationNodeKindRules)

        return nodeKindDict[str(res) + "_" + self.integration_option]
    
    def execute_min_count_integration(self, min_count_list: list) -> list:
        if self.integration_option == 'union':
            minimum = min(min_count_list)
        elif self.integration_option == 'intersection':
            minimum = max(min_count_list)

        return [minimum] if minimum != None else []
    
    def execute_max_count_integration(self, max_count_list: list) -> list:
        if self.integration_option == 'union':
            maximum = max(max_count_list)
        elif self.integration_option == 'intersection':
            maximum = min(max_count_list)

        return [maximum] if maximum != None else []
    
    
    def get_min_bound(self, minExclusive: list = [], minInclusive: list = []) -> dict:
        result = {}

        all_min = []

        if minExclusive:
            all_min.append(('exclusive', max(minExclusive) if self.integration_option == 'intersection' else min(minExclusive)))
        if minInclusive:
            all_min.append(('inclusive', max(minInclusive) if self.integration_option == 'intersection' else min(minInclusive)))

        if all_min:
            min_result = max(all_min, key=lambda x: x[1]) if self.integration_option == 'intersection' else min(all_min, key=lambda x: x[1])
            result['min'] = min_result[1]
            result['min_type'] = min_result[0]

        return result

    def get_max_bound(self, maxExclusive: list = [], maxInclusive: list = []) -> dict:
        result = {}

        all_max = []

        if maxExclusive:
            all_max.append(('exclusive', min(maxExclusive) if self.integration_option == 'intersection' else max(maxExclusive)))
        if maxInclusive:
            all_max.append(('inclusive', min(maxInclusive) if self.integration_option == 'intersection' else max(maxInclusive)))

        if all_max:
            max_result = min(all_max, key=lambda x: x[1]) if self.integration_option == 'intersection' else max(all_max, key=lambda x: x[1])
            result['max'] = max_result[1]
            result['max_type'] = max_result[0]

        return result

    # min_output = self.get_min_bound(
    #     minInclusive=[3]
    # )

    # max_output = self.get_max_bound(
    #     maxExclusive=[9],
    #     maxInclusive=[10]
    # )