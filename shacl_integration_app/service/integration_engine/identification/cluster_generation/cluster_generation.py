from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster, PropertyAxiomCluster, Axiom
from rdflib import Graph
from rdflib.query import Result
from shacl_integration_app.repository.wrappers import get_time
from shacl_integration_app.repository.constants import sparql_queries
from shacl_integration_app.service.integration_engine.identification.cluster_generation.tuple_processor import TupleProcessor
from shacl_integration_app.repository.constants.constants import global_aligned_properties, global_aligned_properties_res
import os
from collections import defaultdict
import json
import re

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
                                                             node_axiom_cluster_list=self.node_axiom_cluster_generation(target_node=target_node, 
                                                             extraction_results=extraction_results),
                                                             property_cluster_list=self.property_cluster_generation(target_node=target_node, new_hlt_tuples_unaligned=new_hlt_tuples_unaligned, new_hlt_tuples_aligned=new_hlt_tuples_aligned, extraction_results=extraction_results))
            # print(concept_cluster)
        
        
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
    
    
    def node_axiom_cluster_generation(self, target_node: tuple[tuple[str]], extraction_results: dict) -> list[Cluster]:
        axiom_list: list[Axiom] = []
        axiom_logical_list: list[Axiom] = []
        for node in target_node:
            for res in extraction_results["shape_extractions"]:
                if res["root"] == node[0]:
                    for triple in res["triples"]:
                        not_list_with_property: list[str] = ['http://www.w3.org/ns/shacl#property', 'http://www.w3.org/ns/shacl#or', 'http://www.w3.org/ns/shacl#and', 'http://www.w3.org/ns/shacl#xone', 'http://www.w3.org/ns/shacl#not', 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
                        if triple["subject"] == node[0] and triple["predicate"] not in not_list_with_property:
                            axiom_list.append(Axiom(pred=triple["predicate"], obj=triple["object"]))

                        not_list_without_property: list[str] = ['http://www.w3.org/ns/shacl#or', 'http://www.w3.org/ns/shacl#and', 'http://www.w3.org/ns/shacl#xone', 'http://www.w3.org/ns/shacl#not']
                        if triple["subject"] == node[0] and triple["predicate"] in not_list_without_property:
                            logic_constraint = [triple2["object"] for triple2 in res["triples"] if triple2["subject"] == triple["object"] and triple2["predicate"] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest']
                            if logic_constraint:
                                match = re.search(r'\d+$', logic_constraint[0])
                                counter: int = None
                                if match:
                                    counter: int = int(match.group()) - 2 # take last number of blank node and subtract 2
                                if counter:
                                    logic_list: list[str] = [logic_constraint[0][:-1] + str(i) for i in range(1, counter + 1)]
                                    [axiom_logical_list.append(Axiom(pred=triple2["predicate"],
                                                                    obj=triple2["object"],
                                                                    link=triple2["subject"],
                                                                    logical_operator=triple["predicate"]
                                                                    .replace(self.get_namespace(triple["predicate"]), "")
                                                                    .replace("#",  "")))
                                                                    for triple2 in res["triples"] if triple2["subject"] in logic_list and triple2["predicate"] not in not_list_with_property]
                        
        # Dictionary to group axioms by predicate
        grouped_axioms = defaultdict(list)
        grouped_logical_axioms = defaultdict(list)

        # Iterate through the axioms and group them by predicate
        for axiom in axiom_list:
            grouped_axioms[axiom.pred].append(axiom)

        for axiom in axiom_logical_list:
            grouped_logical_axioms[axiom.pred].append(axiom)
        
        result_dict: list = []
        for grouped_axiom in [grouped_axioms, grouped_logical_axioms]:
            for axiom in grouped_axiom.values():
                cluster = {
                    "constraint": axiom[0].pred,
                    "axioms": [
                        {"obj": ax.obj, "logical_operator": ax.logical_operator} for ax in axiom
                    ]
                }
                # Remove duplicate axioms
                cluster['axioms'] = [dict(t) for t in {tuple(d.items()) for d in cluster['axioms']}]
                existing_cluster = next((elem for elem in result_dict if elem["constraint"] == cluster["constraint"]), None)
                if existing_cluster:
                    existing_cluster["axioms"].extend(cluster["axioms"])
                else:
                    result_dict.append(cluster)
                
        cluster_list: list[Cluster] = [NodeAxiomCluster(concept=res["constraint"],
                                                        axiom_list=res["axioms"])
                                                        for res in result_dict]
          
        return cluster_list
    

    def property_cluster_generation(self, target_node: tuple[tuple[str]], new_hlt_tuples_unaligned: list[list[tuple[str]]], new_hlt_tuples_aligned: list[list[tuple[str]]], extraction_results: dict) -> list[Cluster]:
        axiom_list, axiom_logical_list = self.property_axiom_cluster_generation(target_node=target_node, extraction_results=extraction_results)
                                
        # ANALYSE HERE IF THERE ARE PROPERTY SHAPES THAT ARE ALIGNED


        if axiom_list != []:
            print(axiom_list)
        # if axiom_logical_list != []:
        #     print(axiom_logical_list)

        return []



    def property_axiom_cluster_generation(self, target_node: tuple[tuple[str]], extraction_results: dict) -> tuple[list[Axiom], list[Axiom]]:
        axiom_list: list[Axiom] = []
        axiom_logical_list: list[Axiom] = []
        for node in target_node:
            for res in extraction_results['shape_extractions']:
                if res["root"] == node[0]:
                    for triple in res["triples"]:
                        stop_word_list: list[str] = ['http://www.w3.org/ns/shacl#or', 'http://www.w3.org/ns/shacl#and', 'http://www.w3.org/ns/shacl#xone', 'http://www.w3.org/ns/shacl#not', 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
                        logical_stop_word_list: list[str] = ['http://www.w3.org/ns/shacl#or', 'http://www.w3.org/ns/shacl#and', 'http://www.w3.org/ns/shacl#xone', 'http://www.w3.org/ns/shacl#not']
                        if triple["subject"] == node[0] and triple["predicate"] == 'http://www.w3.org/ns/shacl#property':
                            property_triples = [[triple2['predicate'], triple2["object"]] for triple2 in res["triples"] if triple2["subject"] == triple["object"] and triple2["subject"] == triple['object'] and triple2["predicate"] not in stop_word_list] # This works
                            # print(property_triples)
                            [axiom_list.append(Axiom(pred=property_triple[0], obj=property_triple[1], link=triple["subject"])) for property_triple in property_triples if property_triples] # This also works
                            
                            logic_constraints = [[triple2["predicate"], triple2["object"]] for triple2 in res["triples"] if triple2["subject"] == triple["object"] and triple2["predicate"] in logical_stop_word_list] # This also works

                            logic_triples : dict = None
                            if logic_constraints:
                                for logic_c in logic_constraints:
                                    first_triple: str = None
                                    rest_triple: str = None
                                    for triple2 in res["triples"]:
                                        if triple2["subject"] == logic_c[1] and triple2["predicate"] not in stop_word_list and triple2["predicate"] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#first':
                                            first_triple = triple2["object"]
                                        if triple2["subject"] == logic_c[1] and triple2["predicate"] not in stop_word_list and triple2["predicate"] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest':
                                            rest_triple = triple2["object"]
                                        if first_triple and rest_triple:
                                            logic_triples = {}
                                            logic_triples["logical_operator"] = logic_c[0]
                                            logic_triples["first_triple"] = first_triple
                                            logic_triples["rest_triple"] = rest_triple

                            if logic_triples:
                                match_first = re.search(r'\d+$', logic_triples["first_triple"])
                                match_first_without_num = re.sub(r'\d+$', '', logic_triples["first_triple"])
                                match_rest = re.search(r'\d+$', logic_triples["rest_triple"])
                                counter: int = None
                                if match_first and match_rest:
                                    counter: int = int(match_rest.group()) - 2
                                    logic_list: list[str] = [match_first_without_num + str(i) for i in range(int(match_first.group()), counter + 1)]
                                    for logic in logic_list:
                                        axiom_logical_list.extend([Axiom(pred=triple2["predicate"],
                                                                    obj=triple2["object"],
                                                                    link=logic,
                                                                    logical_operator=logic_triples["logical_operator"]
                                                                    .replace(self.get_namespace(triple["predicate"]), "")
                                                                    .replace("#",  ""))
                                                                    for triple2 in res["triples"] if triple2["subject"] == logic and triple2["predicate"] not in stop_word_list])
        return axiom_list, axiom_logical_list

    
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



