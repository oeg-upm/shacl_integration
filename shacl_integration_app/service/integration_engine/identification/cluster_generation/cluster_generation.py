from shacl_integration_app.repository.models import Cluster
from rdflib import Graph
from shacl_integration_app.repository.wrappers import get_time

class ClusterGeneration:
    def __init__(self, ontology_list: list[str], tuple_result_list: Graph, alignment_reference: str = None) -> None:
        self.ontology_list : list[str] = ontology_list
        self.tuple_result_list : Graph = tuple_result_list
        self.alignment_reference : str = alignment_reference
        self.cluster_result_list : list[Cluster] = []
        self.ontology_alignment_results : Graph = Graph()

    @get_time
    def execute_alignment(self) -> Graph:
        print(self.alignment_reference)
        if self.alignment_reference is None:
            self.ontology_alignment_results = None
            return self.ontology_alignment_results
        else:
            self.ontology_alignment_results.parse(self.alignment_reference)
            return self.ontology_alignment_results
        
    @get_time        
    def execute_transitive_alignment(self) -> Graph:
        return self.tuple_result_list


    @get_time
    def execute_cluster_generation(self) -> list[Cluster]:
        self.execute_alignment()
        self.execute_transitive_alignment()
        return self.cluster_result_list