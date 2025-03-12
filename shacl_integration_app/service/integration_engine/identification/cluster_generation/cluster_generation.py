from shacl_integration_app.repository.models import Cluster
from rdflib import Graph

class ClusterGeneration:
    def __init__(self, ontology_list: list[str], alignment_reference: str, tuple_result_list: Graph) -> None:
        self.ontology_list : list[str] = ontology_list
        self.cluster_result_list : list[Cluster] = []
        self.alignment_reference : str = alignment_reference
        self.tuple_result_list : Graph = tuple_result_list
        self.ontology_alignment_results : Graph = Graph()

    def execute_alignment(self) -> Graph:
        if self.alignment_reference is None:
            self.ontology_alignment_results = None
            return self.ontology_alignment_results
        else:
            self.ontology_alignment_results.parse(self.alignment_reference)
            return self.ontology_alignment_results
        
    def execute_transitive_alignment(self) -> Graph:
        return self.tuple_result_list

    def execute_cluster_generation(self) -> list[Cluster]:
        self.execute_alignment()
        self.execute_transitive_alignment()
        return self.cluster_result_list