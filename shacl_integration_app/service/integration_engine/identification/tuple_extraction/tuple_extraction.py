from rdflib import Graph
from rdflib.query import Result
from shacl_integration_app.repository.constants import sparql_queries
from shacl_integration_app.service.integration_engine.identification.tuple_extraction.run_query import run_query_for_target
from shacl_integration_app.repository.wrappers import get_time
import sys
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.stdout.flush()

class TupleExtraction:
    def __init__(self, input_tuples: list[tuple[str, str]]) -> None:
        self.input_tuples: list[tuple[str, str]] = input_tuples
        self.tuple_result_set: set[tuple[str]] = set()  # Use a set for better performance

    @get_time
    def execute_tuple_extraction(self) -> list[tuple[str]]:
        for tup in self.input_tuples:
            # Parse graphs once
            ontology_graph: Graph = Graph().parse(tup[0])
            shapes_graph: Graph = Graph().parse(tup[1])

            # Execute all queries and collect results
            result_list = [
                self.obtain_node_transE_tuples(graph=shapes_graph, node_queries=sparql_queries.node_queries_target_class),
                self.obtain_node_transE_tuples(graph=shapes_graph, node_queries=sparql_queries.node_queries_subjects_objects),
                self.obtain_property_transE_tuples(graph=shapes_graph, sparql_query=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE, value_list=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE_values),
                self.obtain_property_transE_tuples(graph=shapes_graph, sparql_query=sparql_queries.SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE, value_list=sparql_queries.SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE_values),
                # self.final_transE_tuples(queries_result=self.obtain_node_transE_tuples(graph=shapes_graph, node_queries=sparql_queries.node_queries_subjects_objects), ontology=ontology_graph),
                # self.final_transE_tuples(queries_result=self.obtain_property_transE_tuples(graph=shapes_graph, sparql_query=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE, value_list=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE_values), ontology=ontology_graph),
                # self.final_transE_tuples(queries_result=self.obtain_property_transE_tuples(graph=shapes_graph, sparql_query=sparql_queries.SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE, value_list=sparql_queries.SPARQL_QUERY_REAL_PROPERTY_PATH_SHAPE_values), ontology=ontology_graph),
            ]

            # Add results to the set
            for result in result_list:
                if result:
                    self.tuple_result_set.update(result)

        # Filter invalid tuples
        self.tuple_result_set = {
            item for item in self.tuple_result_set
            if 'http' in item[0] and (item[2] == 'None' or 'http' in item[2])
        }

        # Write the result to a file
        # with open("tuple_result_list.txt", "w") as f:
        #     f.writelines(f"{str(item)}\n" for item in self.tuple_result_set)

        return list(self.tuple_result_set)

    def obtain_node_transE_tuples(self, graph: Graph, node_queries: list[list[str]]) -> list[tuple[str]]:
        return [
            transE_tuple
            for query in node_queries
            for transE_tuple in self.obtain_transE_tuples(graph=graph, sparql_query=query[0], value_list=query[1])
        ]

    def obtain_property_transE_tuples(self, graph: Graph, sparql_query: str, value_list: str) -> list[tuple[str]]:
        return [
            transE_tuple
            for transE_tuple in self.obtain_transE_tuples(graph=graph, sparql_query=sparql_query, value_list=value_list)
            if transE_tuple[1] != 'None'
        ]

    @staticmethod
    def obtain_transE_tuples(graph: Graph, sparql_query: str, value_list: list[str, str]) -> list[tuple[str]]:
        results: Result = graph.query(sparql_query)
        return [
            (str(row[value_list[0]]), str(row[value_list[1]]), str(value_list[2]))
            for row in results
        ]

    # @staticmethod
    # def final_transE_tuples(queries_result: list[tuple[str]], ontology: Graph) -> list[tuple[str]]:
    #     try:
    #         import tempfile
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl") as temp_file:
    #             ontology.serialize(destination=temp_file.name, format="ttl")
    #             ontology_path = temp_file.name

    #         targets = [res[1] for res in queries_result if res[1] != 'None']
    #         final_results = []

    #         with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    #             futures = [executor.submit(run_query_for_target, target, ontology_path) for target in targets]

    #             for future in as_completed(futures):
    #                 results = future.result()
    #                 final_results.extend(results)

    #         return final_results

    #     except Exception as e:
    #         print(e)
    #         return []