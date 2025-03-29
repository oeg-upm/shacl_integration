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
import hashlib

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
        target_nodes_unaligned: list[tuple[tuple[str]]] = [elem for elem in new_hlt_tuples_unaligned if elem[2] == 'http://www.w3.org/ns/shacl#targetClass']

        for target_node in target_nodes_aligned:
            concept_cluster: ConceptCluster = ConceptCluster(concept=target_node[0][1]
                                                             .replace(self.get_namespace(target_node[0][1]), "")
                                                             .replace("#",  "")
                                                             .replace("/", ""),
                                                             concept_list=[elem[1] for elem in target_node], 
                                                             node_axiom_cluster_list=self.node_axiom_cluster_generation(target_node=target_node, 
                                                             extraction_results=extraction_results),
                                                             property_cluster_list=self.property_cluster_generation(target_node=target_node,
                                                                                                                    new_hlt_tuples_aligned=new_hlt_tuples_aligned,
                                                                                                                    extraction_results=extraction_results))
        
            self.cluster_result_list.append(concept_cluster)
        
        for target_node in target_nodes_unaligned:
            concept_cluster: ConceptCluster = ConceptCluster(concept=target_node[1]
                                                             .replace(self.get_namespace(target_node[1]), "")
                                                             .replace("#",  "")
                                                             .replace("/", ""),
                                                             concept_list=[target_node[1]], 
                                                             node_axiom_cluster_list=self.node_axiom_cluster_generation(target_node=[target_node], # Aquí el target node es una única tupla, por lo que lo metemos en una lista y así vale el mismo código
                                                             extraction_results=extraction_results),
                                                             property_cluster_list=self.property_cluster_generation(target_node=[target_node], # Aquí el target node es una única tupla, por lo que lo metemos en una lista y así vale el mismo código
                                                                                                                    new_hlt_tuples_aligned=new_hlt_tuples_aligned,
                                                                                                                    extraction_results=extraction_results))
        
            self.cluster_result_list.append(concept_cluster)
        
        
        
        # with open('new_hlt_tuples_aligned.txt', 'w') as f:
        #     for item in new_hlt_tuples_aligned:
        #         f.write("%s\n" % str(item))
                
        # with open('new_hlt_tuples_unaligned.txt', 'w') as f:
        #     for item in new_hlt_tuples_unaligned:
        #         f.write("%s\n" % str(item))

        # with open('extraction_results.json', 'w') as f:
        #     f.write(json.dumps(extraction_results, indent=4))
        
        # with open('cluster_result_list.txt', 'w') as f:
        #     f.write(str(self.cluster_result_list))

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
    

    def property_cluster_generation(self, target_node: tuple[tuple[str]], new_hlt_tuples_aligned: list[list[tuple[str]]], extraction_results: dict) -> list[Cluster]:
        axiom_list, axiom_logical_list = self.property_axiom_cluster_generation(target_node=target_node, extraction_results=extraction_results)

        axiom_list.extend(axiom_logical_list)
                                
        # # ANALYSE HERE IF THERE ARE PROPERTY SHAPES THAT ARE ALIGNED

        res = []
        if axiom_list != []:
            # print(axiom_list)
            # for axiom in axiom_list:
            #     if axiom.obj == "http://www.w3.org/ns/ssn/hasProperty":
            #         res = self.group_axioms_by_path(axioms=axiom_list, aligned_paths=new_hlt_tuples_aligned)
            #         print("here")
            #         with open ('axiom_list.txt', 'w') as f:
            #             f.write(str(res))
            res = self.group_axioms_by_path(axioms=axiom_list, aligned_paths=new_hlt_tuples_aligned)
        return res


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
                            property_triples = [[triple2['predicate'], triple2["object"], triple2["subject"]] for triple2 in res["triples"] if triple2["subject"] == triple["object"] and triple2["subject"] == triple['object'] and triple2["predicate"] not in stop_word_list] # This works
                            
                            [axiom_list.append(Axiom(pred=property_triple[0], obj=property_triple[1], link=property_triple[2])) for property_triple in property_triples if property_triples] # This also works
                            
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
                                        axiom_class = [Axiom(pred=triple2["predicate"],
                                                                    obj=triple2["object"],
                                                                    link=logic,
                                                                    logical_operator=logic_triples["logical_operator"]
                                                                    .replace(self.get_namespace(triple["predicate"]), "")
                                                                    .replace("#",  ""))
                                                                    for triple2 in res["triples"] if triple2["subject"] == logic and triple2["predicate"] not in stop_word_list]
                                        
                                        axiom_logical_list.extend(axiom_class)
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


    def group_axioms_by_path(self, axioms, aligned_paths):
        path_to_link = defaultdict(list)
        grouped_axioms = defaultdict(lambda: defaultdict(list))
        link_to_paths = defaultdict(set)

        # Recorremos los axiomas para obtener el mapeo de links a paths
        for axiom in axioms:
            if axiom.pred.endswith("#path"):
                path_to_link[axiom.link].append(axiom.obj)
                link_to_paths[axiom.obj].add(axiom.link)

        # Mapeo de paths alineados
        aligned_map = {}
        for paths_group in aligned_paths:
            unified_paths = set()
            for _, path_value, path_type in paths_group:
                if path_type == "http://www.w3.org/ns/shacl#path":
                    unified_paths.add(path_value)
            for path in unified_paths:
                aligned_map[path] = unified_paths

            # Guardamos en el diccionario global solo cuando se encuentra un aligned_path
            if unified_paths:
                unified_paths_id = hashlib.sha1("".join(unified_paths).encode("utf-8")).hexdigest()
                global_aligned_properties_res[unified_paths_id] = {
                    "aligned_path": unified_paths
                }

        # Agrupar axiomas según los paths alineados
        for axiom in axioms:
            if axiom.link in path_to_link and not axiom.pred.endswith("#path"):
                paths = set(path_to_link[axiom.link])
                aligned_paths_set = set()
                for path in paths:
                    # Verifica si el path está alineado
                    aligned_paths_set.update(aligned_map.get(path, set()))

                # Solo agrupar si hay rutas alineadas
                if aligned_paths_set:
                    grouped_axioms[tuple(sorted(aligned_paths_set))][axiom.pred].append(axiom.obj)
                else:
                    # Si no está alineado, no agrupar
                    grouped_axioms[tuple(sorted(paths))][axiom.pred].append(axiom.obj)

        # Función para determinar el operador lógico predominante
        def get_predominant_operator(operators):
            precedence = {"or": 1, "and": 2, "not": 3, "xone": 4}
            max_precedence = float("inf")
            predominant = None
            if operators != {None}:
                for op in operators:
                    op_precedence = precedence.get(op, float("inf"))
                    if op_precedence < max_precedence:
                        max_precedence = op_precedence
                        predominant = op
            else:
                predominant = "None"
            return predominant

        # Formar el resultado con las claves necesarias
        result = []
        for path, predicates in grouped_axioms.items():
            group = {"path": list(path), "axioms": []}

            # Obtener todos los operadores lógicos en los axiomas del grupo
            operators = set()
            logical_operator = None

            # Iterate over predicates and objects to obtain logical operators
            for pred, objs in predicates.items():
                
                for obj in objs:
                    # Here it filters to ensure that only the axioms of the current group are processed
                    for axiom in axioms:
                        if axiom.pred == pred and axiom.obj == obj:
                            operators.add(axiom.logical_operator)

            # Determinar el operador lógico predominante
            logical_operator = get_predominant_operator(operators)
            if logical_operator:
                group["logical_operator"] = logical_operator

            # Añadir los axiomas al grupo
            for pred, objs in predicates.items():
                # remove duplicates
                objs = list(set(objs))
                group["axioms"].append({"predicate": pred, "objects": objs})

            # Crear PropertyCluster incluso si no se encuentra en el diccionario global
            property_cluster = PropertyCluster(
                property_axiom_cluster_list=[group],
                concept_list=list(path),
            )

            # Si encontramos una coincidencia en el diccionario global, asignamos el id
            for cluster_id, cluster_info in global_aligned_properties_res.items():
                if set(path).issubset(cluster_info["aligned_path"]):
                    property_cluster.id = cluster_id  # Asignar el id del diccionario global
                    break  # Si ya encontramos el id, no es necesario seguir buscando

            # Añadir el PropertyCluster al resultado
            result.append(property_cluster)

        return result