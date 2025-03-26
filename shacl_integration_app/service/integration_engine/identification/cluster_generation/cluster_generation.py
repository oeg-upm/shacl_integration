from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster, PropertyAxiomCluster, Axiom
from rdflib import Graph
from rdflib.query import Result
from shacl_integration_app.repository.wrappers import get_time
from shacl_integration_app.repository.constants import sparql_queries
from shacl_integration_app.service.integration_engine.identification.cluster_generation.tuple_processor import TupleProcessor
import os
from collections import defaultdict
import json

# This Python class `ClusterGeneration` is designed to generate clusters based on ontology alignment
# results and transitive alignment.
class ClusterGeneration:
    def __init__(self, ontology_list: list[str], shapes_list: list[str], tuple_result_list: list[tuple[str]], alignment_reference: str = None) -> None:
        self.ontology_list : list[str] = ontology_list
        self.shapes_list : list[str] = shapes_list
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
        """
        The function `execute_transitive_alignment` processes alignment tuples and generates new
        alignment tuples based on certain conditions.
        :return: The `execute_transitive_alignment` method returns a list of tuples containing alignment
        pairs that have been identified based on certain conditions and operations performed within the
        method.
        """
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
                if len(common) == 2 and len(t1) == 3 and len(t2) == 3:
                    diff_t1: str | tuple = list(t1 - common)[0]
                    diff_t2: str | tuple = list(t2 - common)[0]
                    if type(diff_t1) is not tuple and type(diff_t2) is not tuple:
                        namespace_1 = self.get_namespace(diff_t1)
                        namespace_2 = self.get_namespace(diff_t2)
                        if namespace_1 != namespace_2:
                            self.alignment_tuples_result.append((diff_t1, diff_t2))
        return self.alignment_tuples_result


    def get_namespace(self, uri: str) -> str:
        """
        This Python function extracts the namespace from a given URI.
        
        :param uri: The `uri` parameter is a string that represents a Uniform Resource Identifier (URI)
        for which we want to extract the namespace
        :type uri: str
        :return: The `get_namespace` function takes a URI as input and returns the namespace part of the
        URI. If the URI contains a '#' symbol, it splits the URI at the '#' symbol and returns the part
        before the '#'. If the URI does not contain a '#', it splits the URI at the last '/' symbol and
        returns all parts except the last one.
        """
        if '#' in uri:
            return uri.split('#')[0]
        else:
            return '/'.join(uri.split('/')[:-1])

    @get_time
    def execute_cluster_generation(self) -> list[Cluster]:
        """
        This function executes cluster generation after performing alignment and transitive alignment if
        needed.
        :return: The method `execute_cluster_generation` returns a list of Cluster objects.
        """
        self.execute_alignment()
        if self.alignment_reference is None:
            pass
        else:
            self.execute_transitive_alignment()
            self.cluster_generation()
        return self.cluster_result_list
    
    def cluster_generation(self) -> list[Cluster]:
        # self.shapes_list
        # tuple_result_list
        # self.alignment_tuples_result

        # Step 1: Search for alignments in the tuple_result_list for node shapes
        path_list: list[str] = ['http://www.w3.org/ns/shacl#targetClass', 'http://www.w3.org/ns/shacl#path', 'http://www.w3.org/ns/shacl#targetObjectsOf', 'http://www.w3.org/ns/shacl#targetSubjectsOf']
        hlt_node_tuples: list[tuple[str]] = [tup for tup in self.tuple_result_list if tup[2] in path_list]
        hlt_property_tuples: list[tuple[str]] = [tup for tup in self.tuple_result_list if tup[2] not in path_list]
        new_hlt_tuples_aligned: list[list[tuple[str]]] = []
        new_hlt_tuples_unaligned: list[tuple[str]] = []

        new_hlt_tuples_aligned, new_hlt_tuples_unaligned = self.extract_alignments_from_tuples(hlt_node_tuples=hlt_node_tuples,
                                                                                               new_hlt_tuples_aligned=new_hlt_tuples_aligned,
                                                                                                new_hlt_tuples_unaligned=new_hlt_tuples_unaligned)
        
        new_hlt_tuples_aligned, new_hlt_tuples_unaligned = self.extract_alignments_from_tuples(hlt_node_tuples=hlt_property_tuples,
                                                                                               new_hlt_tuples_aligned=new_hlt_tuples_aligned,
                                                                                                new_hlt_tuples_unaligned=new_hlt_tuples_unaligned)

        processor = TupleProcessor()
        new_hlt_tuples_aligned = processor.process_tuples(new_hlt_tuples_aligned)

        # Step 2: Extract shapes from shacl shapes 

        extraction_results: dict = {
            "shape_extractions" : []
        }
        for shape_file in self.shapes_list:
            shape: Graph = Graph()
            shape.parse(shape_file)
            results: Result = shape.query(sparql_queries.SPARQL_QUERY_EXTRACT_SHAPES)
            if results:
                extraction_results["shape_extractions"].extend(self.process_sparql_results(results))

        # Step 3: Generate clusters

        target_nodes_aligned: list[tuple[tuple[str]]] = [elem for elem in new_hlt_tuples_aligned if elem[0][2] == 'http://www.w3.org/ns/shacl#targetClass']

        for target_node in target_nodes_aligned:
            concept_cluster: ConceptCluster = ConceptCluster(concept=target_node[0][1]
                                                             .replace(self.get_namespace(target_node[0][1]), "")
                                                             .replace("#",  "")
                                                             .replace("/", ""),
                                                             concept_list=[elem[1] for elem in target_node], 
                                                             node_axiom_cluster_list=self.node_axiom_cluster_generation(target_node=target_node, new_hlt_tuples_aligned=new_hlt_tuples_aligned, extraction_results=extraction_results),
                                                             property_cluster_list=self.property_cluster_generation(target_node=target_node, new_hlt_tuples_aligned=new_hlt_tuples_aligned, extraction_results=extraction_results))
            print(concept_cluster)
        
        
        # with open('new_hlt_tuples_aligned.txt', 'w') as f:
        #     for item in new_hlt_tuples_aligned:
        #         f.write("%s\n" % str(item))
                
        # with open('new_hlt_tuples_unaligned.txt', 'w') as f:
        #     for item in new_hlt_tuples_unaligned:
        #         f.write("%s\n" % str(item))

        # with open('extraction_results.json', 'w') as f:
        #     f.write(json.dumps(extraction_results, indent=4))
            

        # self.cluster_result_list
        return self.cluster_result_list
    
    
    def node_axiom_cluster_generation(self, target_node: tuple[tuple[str]], new_hlt_tuples_aligned: list[list[tuple[str]]], extraction_results: dict) -> list[Cluster]:
        return []

    def property_cluster_generation(self, target_node: tuple[tuple[str]], new_hlt_tuples_aligned: list[list[tuple[str]]], extraction_results: dict) -> list[Cluster]:
        return []

    def property_axiom_cluster_generation(self) -> Cluster:
        pass

    
    def process_sparql_results(self, query_results: Result) -> list[dict[str, list[dict[str, str]]]]:
        """
        Processes SPARQL query results to extract and organize data into a structured format.
        
        :param query_results: SPARQL query results containing rows with root, subject, predicate, and object.
        :return: A list of dictionaries, each representing a root and its associated triples.
        """
        data = {}
        all_roots = set()
        subj_objs = defaultdict(set)

        for row in query_results:
            root = str(row.root)
            subject = str(row.subj)
            predicate = str(row.pred)
            obj = str(row.obj)

            if root not in data:
                data[root] = {"root": root, "triples": []}

            data[root]["triples"].append({
                "subject": subject,
                "predicate": predicate,
                "object": obj
            })

            all_roots.add(root)
            subj_objs[root].update([subject, obj])

        roots_to_remove = {
            root for root in all_roots
            if any(root in subj_objs[other_root] for other_root in all_roots if root != other_root)
        }

        for root in roots_to_remove:
            data.pop(root, None)

        return list(data.values())

    
    def extract_alignments_from_tuples(self, hlt_node_tuples: list[tuple[str]], new_hlt_tuples_aligned: list[list[tuple[str]]], new_hlt_tuples_unaligned: list[tuple[str]]) -> list[list[tuple[str]]]:
        """
        The function `extract_alignments_from_tuples` processes a list of tuples to extract aligned and
        unaligned tuples based on certain conditions.
        
        :param hlt_node_tuples: The `hlt_node_tuples` parameter is a list of tuples where each tuple
        contains two strings. This function seems to iterate over each tuple in `hlt_node_tuples`, check
        for alignments in `alignment_tuples_result`, and then categorize the tuples into
        `new_hlt_tuples_aligned` or `
        :type hlt_node_tuples: list[tuple[str]]
        :param new_hlt_tuples_aligned: The `new_hlt_tuples_aligned` parameter is a list of lists where
        each inner list contains tuples of strings. This parameter is used to store aligned tuples
        extracted from the `hlt_node_tuples` based on certain conditions in the
        `extract_alignments_from_tuples` method
        :type new_hlt_tuples_aligned: list[list[tuple[str]]]
        :param new_hlt_tuples_unaligned: The parameter `new_hlt_tuples_unaligned` in the function
        `extract_alignments_from_tuples` is a list of tuples containing strings. This list is used to
        store the tuples that do not have any alignments based on the logic implemented in the function
        :type new_hlt_tuples_unaligned: list[tuple[str]]
        :return: The function `extract_alignments_from_tuples` returns two lists:
        `new_hlt_tuples_aligned` and `new_hlt_tuples_unaligned`.
        """
        for hlt in hlt_node_tuples:
            new_hlt_node = list(hlt)
            flag: int = 0
            aligned_tuples = []
            for alignment in self.alignment_tuples_result:
                if hlt[1] in alignment:
                    target_alignment = alignment[1] if hlt[1] == alignment[0] else alignment[0]
                    res_alignment: list[tuple[str]] =[elem for elem in hlt_node_tuples if elem[1] == target_alignment]
                    if res_alignment != []:
                        aligned_tuples.extend(res_alignment)
                        flag += 1
            if flag == 1:
                aligned_tuples.append(tuple(new_hlt_node))
                new_hlt_tuples_aligned.append(aligned_tuples)
            else:
                new_hlt_tuples_unaligned.append(hlt)

        return new_hlt_tuples_aligned, new_hlt_tuples_unaligned



