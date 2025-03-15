from rdflib import Graph
from rdflib.query import Result
from shacl_integration_app.repository.constants import sparql_queries
from shacl_integration_app.repository.wrappers import get_time
import sys
sys.stdout.flush()

class TupleExtraction:
    def __init__(self, input_tuples: list[tuple[str, str]]) -> None:
        self.input_tuples: list[tuple[str, str]] = input_tuples
        self.tuple_result_list: list[tuple[str]] = []

    @get_time
    def execute_tuple_extraction(self) -> Graph:
        for tup in self.input_tuples:
            # Execute the SPARQL query
            ontology_graph: Graph = Graph().parse(tup[0])
            shapes_graph: Graph = Graph().parse(tup[1])

            # Node queries target class
            node_queries_result_target_class: list[tuple[str]] = self.obtain_node_transE_tuples(graph=shapes_graph, node_queries=sparql_queries.node_queries_target_class)

            # Node queries target subjects and objects of
            node_queries_result_subjects_objects: list[tuple[str]] = self.obtain_node_transE_tuples(graph=shapes_graph, node_queries=sparql_queries.node_queries_subjects_objects)

            # Property queries
            property_queries_result: list[tuple[str]] = self.obtain_property_transE_tuples(graph=shapes_graph)

            # TargetSubjectsOf & TargetObjectsOf query onto
            final_transE_subj_obj_tuples_result: list[tuple[str]] = self.final_transE_tuples(queries_result=node_queries_result_subjects_objects, ontology=ontology_graph)

            # Property shapes query onto
            final_transE_property_tuples_result: list[tuple[str]] = self.final_transE_tuples(queries_result=property_queries_result, ontology=ontology_graph)

            result_list: list[list[tuple[str]]] = [node_queries_result_target_class, node_queries_result_subjects_objects, property_queries_result, final_transE_subj_obj_tuples_result, final_transE_property_tuples_result]
            [self.tuple_result_list.extend(item) for item in result_list if item != None and len(item) > 0]

        # Remove duplicates
        self.tuple_result_list = list(set(self.tuple_result_list))

        # Remove tuples with not correct values
        for item in self.tuple_result_list[:]:  # Create a copy of the list
            if 'http' not in item[0]:
                self.tuple_result_list.remove(item)
            elif 'http' not in item[2] and item[2] != 'None':
                self.tuple_result_list.remove(item)
        
        # Write the result to a file
        with open("tuple_result_list.txt", "w") as f:
            [f.write(str(item) + '\n') for item in self.tuple_result_list]
            f.close()

        return self.tuple_result_list
    
    
    def obtain_node_transE_tuples(self, graph: Graph, node_queries: list[list[str]]) -> list[tuple[str]]:
        node_queries_result: list[tuple[str]] = [
            transE_tuple
            for query in node_queries
            for transE_tuple in self.obtain_transE_tuples(graph=graph,
                                  sparql_query=query[0],
                                  value_list=query[1])
        ]
        return node_queries_result
    
    def obtain_property_transE_tuples(self, graph: Graph) -> list[tuple[str]]:
        property_queries_result: list[tuple[str]] = [
            transE_tuple
            for transE_tuple in self.obtain_transE_tuples(graph=graph,
                                  sparql_query=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE,
                                  value_list=sparql_queries.SPARQL_QUERY_PROPERTY_PATH_SHAPE_values)
        ]
        return property_queries_result
    
    @staticmethod
    def obtain_transE_tuples(graph: Graph, sparql_query: str, value_list: list[str, str]) -> list[tuple[str]]:
        results: Result = graph.query(sparql_query)
        result_tuples: list[tuple[str]] = [(str(row[value_list[0]]), str(row[value_list[1]]), str(value_list[2])) for row in results]
        return result_tuples
    
    @staticmethod
    def final_transE_tuples(queries_result: list[tuple[str]], ontology: Graph) -> list[tuple[str]]:
        
        example = [ontology.query(sparql_queries.SPARQL_QUERY_TARGET_SUBJECTS_OBJECTS_OF_PATH(target_of_path=res[1])) for res in queries_result if ontology.query(sparql_queries.SPARQL_QUERY_TARGET_SUBJECTS_OBJECTS_OF_PATH(target_of_path=res[1])) != []]
        try:
            if len(example) > 0:
                final_transE_tuples_result: list[tuple[str]] = [(str(row[0]), str(row[1]), str(row[2])) for elem in example for row in elem]
                return final_transE_tuples_result
        except Exception as e:
            print(e)