from shacl_integration_app.repository.models.cluster import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster
from shacl_integration_app.repository.constants import count_constants
from rdflib import Graph, Namespace, URIRef, BNode, RDF, Literal
from rdflib.collection import Collection


class SHACLUnificationOperation:
    """
    This class is responsible for the SHACL shapes unification operation of the integration method.
    It receives as input a cluster list with clusters integrated by concepts without inconsistences
    and returns as output the Integrated SHACL Shape.
    """

    def __init__(self, clusters: list[Cluster], integrated_shapes_path: str):
        self.clusters: list[Cluster] = clusters
        self.integrated_shapes_path: str = integrated_shapes_path
        self.integrated_shacl_shape: Graph = Graph()
        # PREFIXES
        self.SH = Namespace('http://www.w3.org/ns/shacl#')
        self.integrated_shacl_shape.bind('sh', 'http://www.w3.org/ns/shacl#')
        self.integrated_shacl_shape.bind('shape_int', 'http://integratedshapes.es#')

    def unify(self):
        self.generate_node_shapes()
        self.generate_property_shapes()
        [self.remove_duplicate_errors(path) for path in ['class', 'datatype', 'pattern']]
        self.remove_multiple_nodeKind()
        self.integrated_shacl_shape.serialize(destination=self.integrated_shapes_path, format='turtle')

    def generate_node_shapes(self):
        for cluster in self.clusters:
            self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), RDF.type, self.SH.NodeShape))
            if len(cluster.concept_list) > 1:
                count_constants.global_integration_counter += 1
            [self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), self.SH.targetClass, URIRef(concept))) for concept in cluster.concept_list]

            [self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), self.SH.property, URIRef(f'http://integratedshapes.es#{property_cluster.id}'))) for property_cluster in cluster.property_cluster_list]

            for node_cluster in cluster.node_axiom_cluster_list:
                predicate: str = node_cluster.concept
                if predicate != 'http://www.w3.org/ns/shacl#targetClass':
                    for axiom in node_cluster.axiom_list:
                        if axiom['logical_operator'] != None and axiom['logical_operator'] != 'None':
                            or_node = BNode()
                            lo: str = axiom['logical_operator']
                            predicate_stop_list = ['http://www.w3.org/ns/shacl#class', 'http://www.w3.org/ns/shacl#path', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#first', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest']
                            if predicate not in predicate_stop_list:
                                # print(f'Adding Axiom: {axiom}')
                                # print(f'Adding Predicate: {predicate}')
                                # print(f'Adding OR node: {or_node}')
                                self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), URIRef(f'http://www.w3.org/ns/shacl#{lo}'), or_node))
                        else:
                            obj = axiom['obj']
                            if predicate=='http://www.w3.org/ns/shacl#nodeKind':
                                print(f'Cluster id: {cluster.id}')
                                print(f'Predicate: {predicate}')
                                print(f'Object: {obj}')
                            if obj != None:
                                if isinstance(obj, str) and obj.startswith("http"):
                                    self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), URIRef(predicate), URIRef(obj)))
                                else:
                                    self.integrated_shacl_shape.add((URIRef(f'http://integratedshapes.es#{cluster.id}'), URIRef(predicate), Literal(obj)))


    def generate_property_shapes(self):
        for cluster in self.clusters:
            for property_cluster in cluster.property_cluster_list:
                shape_uri = URIRef(f'http://integratedshapes.es#{property_cluster.id}')
                self.integrated_shacl_shape.add((shape_uri, RDF.type, self.SH.PropertyShape))
                if len(property_cluster.concept_list) > 1:
                    paths = property_cluster.concept_list
                    if not self.alternative_path_exists(self.integrated_shacl_shape, shape_uri, paths):
                        blankNode = BNode()
                        list_blankNode = BNode()
                        self.integrated_shacl_shape.add((shape_uri, self.SH.path, blankNode))
                        self.integrated_shacl_shape.add((blankNode, self.SH.alternativePath, list_blankNode))
                        Collection(self.integrated_shacl_shape, list_blankNode, [URIRef(p) for p in paths])

                elif len(property_cluster.concept_list) == 1:
                    self.integrated_shacl_shape.add((shape_uri, self.SH.path, URIRef(property_cluster.concept_list[0])))

                for axiom_property in property_cluster.property_axiom_cluster_list:
                    for axiom in axiom_property['axioms']:
                        if len(axiom['objects']) > 1:
                            count_constants.global_integration_counter += 1
                            or_axiom_list: list[str] = ['http://www.w3.org/ns/shacl#class', 'http://www.w3.org/ns/shacl#datatype', 'http://www.w3.org/ns/shacl#pattern']
                            if axiom['predicate'] in or_axiom_list:
                                or_node = BNode()
                                self.integrated_shacl_shape.add((shape_uri, URIRef(axiom['predicate']), or_node))
                                list_blankNode = BNode()
                                self.integrated_shacl_shape.add((or_node, RDF.rest, list_blankNode))
                                Collection(self.integrated_shacl_shape, list_blankNode, [URIRef(o) for o in axiom['objects']])
                            else:
                                for obj in axiom['objects']:
                                    if isinstance(obj, str) and obj.startswith("http"):
                                        self.integrated_shacl_shape.add((shape_uri, URIRef(axiom['predicate']), URIRef(obj)))
                                    else:
                                        self.integrated_shacl_shape.add((shape_uri, URIRef(axiom['predicate']), Literal(obj)))
                        elif len(axiom['objects']) == 1:
                            obj = axiom['objects'][0]
                            if isinstance(obj, str) and obj.startswith("http"):
                                self.integrated_shacl_shape.add((shape_uri, URIRef(axiom['predicate']), URIRef(obj)))
                            else:
                                self.integrated_shacl_shape.add((shape_uri, URIRef(axiom['predicate']), Literal(obj)))





    def alternative_path_exists(self, g, shape_uri, paths_to_check):
        for _, _, path_bnode in g.triples((shape_uri, self.SH.path, None)):
            for _, _, alt_path_list_bnode in g.triples((path_bnode, self.SH.alternativePath, None)):
                existing_paths = list(Collection(g, alt_path_list_bnode))
                if set(existing_paths) == set(URIRef(p) for p in paths_to_check):
                    return True
        return False
    
    def remove_duplicate_errors(self, path):
        for s in self.integrated_shacl_shape.subjects(RDF.type, self.SH.PropertyShape):
            classes = list(self.integrated_shacl_shape.objects(s, self.SH[path]))
            if len(classes) > 1:
                # Paso 2: eliminar las clases actuales
                for c in classes:
                    self.integrated_shacl_shape.remove((s, self.SH[path], c))
                
                # Paso 3: crear [ sh:class <...> ] por cada clase
                class_nodes = []
                for c in classes:
                    bnode = BNode()
                    self.integrated_shacl_shape.add((bnode, self.SH[path], c))
                    class_nodes.append(bnode)
                
                # Paso 4: crear la lista RDF y añadir sh:or
                or_bnode = BNode()
                Collection(self.integrated_shacl_shape, or_bnode, class_nodes)
                self.integrated_shacl_shape.add((s, self.SH["or"], or_bnode))

    def remove_multiple_nodeKind(self):
        preferred_kinds = {
            self.SH.IRIOrLiteral: {self.SH.IRI, self.SH.Literal},
            self.SH.BlankNodeOrIRI: {self.SH.BlankNode, self.SH.IRI},
            self.SH.BlankNodeOrLiteral: {self.SH.BlankNode, self.SH.Literal},
        }

        for s in self.integrated_shacl_shape.subjects(RDF.type, self.SH.PropertyShape):
            node_kinds = list(self.integrated_shacl_shape.objects(s, self.SH.nodeKind))

            if len(node_kinds) <= 1:
                continue  # Nada que simplificar

            # Recorremos las opciones preferidas
            for preferred, covered_set in preferred_kinds.items():
                if preferred in node_kinds:
                    for covered in covered_set:
                        if covered in node_kinds:
                            self.integrated_shacl_shape.remove((s, self.SH.nodeKind, covered))

    
