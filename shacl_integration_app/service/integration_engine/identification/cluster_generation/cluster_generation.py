from shacl_integration_app.repository.models import Cluster
from rdflib import Graph
from rdflib.query import Result
from shacl_integration_app.repository.wrappers import get_time
from shacl_integration_app.repository.constants import sparql_queries
import os

# This Python class `ClusterGeneration` is designed to generate clusters based on ontology alignment
# results and transitive alignment.
class ClusterGeneration:
    def __init__(self, ontology_list: list[str], tuple_result_list: list[tuple[str]], alignment_reference: str = None) -> None:
        self.ontology_list : list[str] = ontology_list
        self.tuple_result_list : list[tuple[str]] = tuple_result_list
        self.alignment_reference : str = alignment_reference
        self.cluster_result_list : list[Cluster] = []
        self.ontology_alignment_results : Graph = Graph()
        self.alignment_tuples_result : list[tuple[str]] = []

    @get_time
    def execute_alignment(self) -> list[tuple[str]]:
        """
        The function `execute_alignment` parses an alignment reference, queries the results based on a
        threshold, and stores the alignment tuples in a list.
        """
        if self.alignment_reference is None:
            self.ontology_alignment_results = None
            # Generate code in order to align ontologies
            pass
        else:
            threshold: str = str(os.getenv('REFERENCE_THRESHOLD', 1.0))
            self.ontology_alignment_results.parse(self.alignment_reference)
            results : Result = self.ontology_alignment_results.query(sparql_queries.SPARQL_QUERY_ALIGNMENT_REFERENCE(threshold))
            self.alignment_tuples_result: list[tuple[str]] = [(str(row['entity1']), str(row['entity2'])) for row in results]
            return self.alignment_tuples_result
        
    @get_time        
    def execute_transitive_alignment(self) -> list[tuple[str]]:
        path_list: list[str] = ['http://www.w3.org/ns/shacl#targetClass', 'http://www.w3.org/ns/shacl#path', 'http://www.w3.org/ns/shacl#targetObjectsOf', 'http://www.w3.org/ns/shacl#targetSubjectsOf']
        hlt_tuples: list[tuple[str]] = [tup for tup in self.tuple_result_list if tup[2] not in path_list]
        new_hlt_tuples = []

        for hlt in hlt_tuples:
            new_hlt = list(hlt)  # Convert the tuple into a list to allow modification of its elements
            flag: int = 0
            for alignment in self.alignment_tuples_result:
                if new_hlt[0] == alignment[0] or new_hlt[0] == alignment[1]:
                    flag += 1
                    new_hlt[0] = (alignment[0], alignment[1])
                if new_hlt[1] == alignment[0] or new_hlt[1] == alignment[1]:
                    flag += 1
                    new_hlt[1] = (alignment[0], alignment[1])
                if new_hlt[2] == alignment[0] or new_hlt[2] == alignment[1]:
                    flag += 1
                    new_hlt[2] = (alignment[0], alignment[1])
            if flag == 2:
                new_hlt_tuples.append(tuple(new_hlt))

        for i in range(len(new_hlt_tuples)):
            for j in range(i + 1, len(new_hlt_tuples)):
                t1 = set(new_hlt_tuples[i])
                t2 = set(new_hlt_tuples[j])
                common: set = t1.intersection(t2)
                if len(common) == 2:
                    diff_t1: str | tuple = list(t1 - common)[0]
                    diff_t2: str | tuple = list(t2 - common)[0]
                    if type(diff_t1) is not tuple and type(diff_t2) is not tuple:
                        namespace_1 = self.get_namespace(diff_t1)
                        namespace_2 = self.get_namespace(diff_t2)
                        if namespace_1 != namespace_2:
                            self.alignment_tuples_result.append((diff_t1, diff_t2))
        return self.alignment_tuples_result


    def get_namespace(self, uri: str) -> str:
        """Extracts the prefix or namespace from a URI."""
        if '#' in uri:
            return uri.split('#')[0]
        else:
            return '/'.join(uri.split('/')[:-1])

    @get_time
    def execute_cluster_generation(self) -> list[Cluster]:
        self.execute_alignment()
        if self.alignment_reference is None:
            pass
        else:
            self.execute_transitive_alignment()
        return self.cluster_result_list
    
    def cluster_generation(self) -> list[Cluster]:
        print(self.alignment_tuples_result)
        return self.execute_cluster_generation()