from rdflib import Graph
from shacl_integration_app.repository.models import Cluster
from shacl_integration_app.service.integration_engine.identification.tuple_extraction import TupleExtraction
from shacl_integration_app.service.integration_engine.identification.cluster_generation import ClusterGeneration
from shacl_integration_app.repository.wrappers import get_time

class Identification:
    def __init__(self, input_tuples:list[tuple[str, str]], alignment_reference:str) -> None:
        self.input_tuples: list[tuple[str, str]] = input_tuples
        self.tuple_result_list: Graph = Graph()
        self.cluster_result_list: list[Cluster] = []
        self.alignment_reference: str = alignment_reference

    @get_time
    def tuple_extraction(self) -> Graph:
        tuple_extraction_activity: TupleExtraction = TupleExtraction(self.input_tuples)
        self.tuple_result_list = tuple_extraction_activity.execute_tuple_extraction()
        return self.tuple_result_list
    

    @get_time
    def cluster_generation(self) -> list[Cluster]:
        cluster_generation_activity: ClusterGeneration = ClusterGeneration(ontology_list=[tup[0] for tup in self.input_tuples],
                                                                           shapes_list=[tup[1] for tup in self.input_tuples],
                                                                           alignment_reference=self.alignment_reference,
                                                                           tuple_result_list=self.tuple_result_list)
        self.cluster_result_list = cluster_generation_activity.execute_cluster_generation()
        # return self.cluster_result_list
        pass
    

    @get_time
    def execute_identification(self) -> list[Cluster]:
        self.tuple_extraction()
        self.cluster_generation()
        return self.cluster_result_list

    