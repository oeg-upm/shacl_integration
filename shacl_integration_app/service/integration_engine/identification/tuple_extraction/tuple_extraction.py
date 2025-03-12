from rdflib import Graph
from shacl_integration_app.repository.constants import sparql_queries
from shacl_integration_app.repository.wrappers import get_time

class TupleExtraction:
    def __init__(self, input_tuples: list[tuple[str, str]]) -> None:
        self.input_tuples: list[tuple[str, str]] = input_tuples
        self.sparql_query: str = None
        self.query_results: Graph = None
        self.tuple_result_list: Graph = None

    @get_time
    def execute_tuple_extraction(self) -> Graph:
        return self.tuple_result_list