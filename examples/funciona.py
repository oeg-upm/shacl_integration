from collections import defaultdict
from dataclasses import dataclass, field
import uuid
import hashlib

# Definimos la clase PropertyCluster
@dataclass
class PropertyCluster:
    property_axiom_cluster_list: list[dict] = field(default_factory=list)
    concept: str = "default_cluster"
    concept_list: list[str] = field(default_factory=list)
    id: str = field(init=False)

    # Constructor personalizado para asignar el id automáticamente
    def __post_init__(self):
        self.id = hashlib.sha1("".join(self.concept_list).encode("utf-8")).hexdigest()  # Generamos un ID único para cada instancia


# Diccionario global para almacenar las tuplas alineadas y sus respectivos IDs
global_aligned_properties_res = {}

class Axiom:
    def __init__(self, pred, obj, logical_operator, link):
        self.pred = pred
        self.obj = obj
        self.logical_operator = logical_operator
        self.link = link

    def __repr__(self):
        return f"Axiom(pred='{self.pred}', obj='{self.obj}', logical_operator='{self.logical_operator}', link='{self.link}')"

def group_axioms_by_path(axioms, aligned_paths):
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
# Ejemplo de uso
axioms = [
    Axiom("http://www.w3.org/ns/shacl#path", "http://www.w3.org/ns/ssn/hasProperty", "and", "nc06f4fc461894fa7b5db5904b10d0d93b20"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#comment", "The property of a feature of interest has to be from the class ssn:Property.", "and", "nc06f4fc461894fa7b5db5904b10d0d93b20"),
    Axiom("http://www.w3.org/ns/shacl#class", "http://www.w3.org/ns/ssn/Property", "and", "nc06f4fc461894fa7b5db5904b10d0d93b20"),
    Axiom("http://www.w3.org/ns/shacl#path", "http://www.w3.org/ns/sosa/hasSample", None, "nc06f4fc461894fa7b5db5904b10d0d93b19"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#comment", "The sample of a feature of interest has to be from the class sosa:Sample.", None, "nc06f4fc461894fa7b5db5904b10d0d93b19"),
    Axiom("http://www.w3.org/ns/shacl#class", "http://www.w3.org/ns/sosa/Sample", None, "nc06f4fc461894fa7b5db5904b10d0d93b19"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "has function", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "Links a feature kind or a device to one of its functions.", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/ns/shacl#class", "https://saref.etsi.org/core/Function", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/ns/shacl#description", "Links a feature kind or a device to one of its functions.", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/ns/shacl#name", "has function", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/ns/shacl#nodeKind", "http://www.w3.org/ns/shacl#BlankNodeOrIRI", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/ns/shacl#path", "https://saref.etsi.org/core/hasFunction", None, "https://astrea.linkeddata.es/shapes#dd7c5ae36318814e4c4bd073b97ad3bb"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "has feature kind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "links a feature of interest to its kind, a feature kind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/ns/shacl#class", "https://saref.etsi.org/core/FeatureKind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/ns/shacl#description", "links a feature of interest to its kind, a feature kind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/ns/shacl#name", "has feature kind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/ns/shacl#nodeKind", "http://www.w3.org/ns/shacl#BlankNodeOrIRI", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/ns/shacl#path", "https://saref.etsi.org/core/hasFeatureKind", None, "https://astrea.linkeddata.es/shapes#a2d1d3c933c9df46a5431f86a2e65948"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "has measurement", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "A relationship between a feature of interest and a measurement about it", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/ns/shacl#class", "https://saref.etsi.org/core/Measurement", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/ns/shacl#description", "A relationship between a feature of interest and a measurement about it", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/ns/shacl#name", "has measurement", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/ns/shacl#nodeKind", "http://www.w3.org/ns/shacl#BlankNodeOrIRI", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/ns/shacl#path", "https://saref.etsi.org/core/hasMeasurement", None, "https://astrea.linkeddata.es/shapes#33647ad48fc226dbafdf80923a8a614b"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "is used for", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/2000/01/rdf-schema#label", "Links a feature kind, feature of interest, or device, to the commodity it is used for", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/ns/shacl#class", "https://saref.etsi.org/core/Commodity", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/ns/shacl#description", "Links a feature kind, feature of interest, or device, to the commodity it is used for", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/ns/shacl#name", "is used for", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/ns/shacl#nodeKind", "http://www.w3.org/ns/shacl#BlankNodeOrIRI", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
    Axiom("http://www.w3.org/ns/shacl#path", "https://saref.etsi.org/core/hasCommodity", None, "https://astrea.linkeddata.es/shapes#44c2e26c59181db9841becf44e7f142f"),
]

aligned_paths = [(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ActuationConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservationCollectionConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservationConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/SamplingConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/resultTimeDomainConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#targetSubjectsOf'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/resultTimeRangeConstraint', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#targetObjectsOf'), ('https://astrea.linkeddata.es/shapes#396b89e7acb1275050dd0f2621960bff', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#4a0fe07d77e1568c9f6119967b7b3d3a', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#60c83dd4552d352d25b92aa351efcc18', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#6b09657a9e2a3494865b52d785bdf325', 'https://saref.etsi.org/core/hasResultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#82ac0ee2607c4d742aa0dafe16a38558', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#c3fb6ea8abe3a615c4212b0c35aadd3c', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#d5f731ed5fd0721dbafe43b1997ef916', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#e61935f1cc0fbdc80be67c061e1cbf71', 'http://www.w3.org/ns/sosa/resultTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#ec4d9be43d49ce4a5080dc148f295395', 'https://saref.etsi.org/core/hasResultTime', 'http://www.w3.org/ns/shacl#path')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ActuatorConstraint', 'http://www.w3.org/ns/sosa/Actuator', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#0ac542fe05bf1e2555a2cb0118d23dc8', 'https://saref.etsi.org/core/Actuator', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#34240d68cbd95d757a10bdbf2fe6b7c0', 'http://www.w3.org/ns/sosa/Actuator', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/SensorConstraint', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/observesDomainConstraint', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#targetSubjectsOf'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/observesRangeConstraint', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#targetObjectsOf'), ('https://astrea.linkeddata.es/shapes#01880a796c2df7337b5c1375c51b5b7d', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#6492d1ff8532f55e1193459c80d86b47', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#7636d31e71ce857caf3a6e5129fd0324', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#9aa8e621cce884491364b00e9cad17b2', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#b86e7e73a18bac08d7a3e6e9a140d2e8', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#c61898f24403ef1f26f4d3767e07d074', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#c78adf719f2fc347d9729f079d86324b', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#d7d1e157a10d4c711970040956ced0eb', 'https://saref.etsi.org/core/observes', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#eef4e9102f8c4e433815a9af41e4f720', 'http://www.w3.org/ns/sosa/observes', 'http://www.w3.org/ns/shacl#path')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/FeatureOfInterestConstraint', 'http://www.w3.org/ns/ssn/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#0a5804dbf271e1e0746c63e997fd9601', 'https://saref.etsi.org/core/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#1fddf06fe6e9b90dfa54ea35fe9edfb7', 'https://saref.etsi.org/core/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#34c0f55f8f3f3c58d9cb361df2984c77', 'https://saref.etsi.org/core/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#37d326bac283bb914605639aa82dfc51', 'http://www.w3.org/ns/ssn/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#811ef72b6ccea344721cf0bcfa6618ba', 'http://www.w3.org/ns/ssn/hasProperty', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#e85f7f569c1b43b31809a79038a33ed0', 'http://www.w3.org/ns/ssn/hasProperty', 'http://www.w3.org/ns/shacl#path')),(('https://astrea.linkeddata.es/shapes#3e18b0f9fac2d3bdcd51a2fdadcbda53', 'http://www.w3.org/2006/time#TemporalEntity', 'http://www.w3.org/ns/shacl#targetClass'),),(('https://astrea.linkeddata.es/shapes#1747a03e68342090168eaf0538c06be3', 'http://www.w3.org/ns/ssn/Property', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#d8fcc404ec3569ab405576151e2c63f9', 'https://saref.etsi.org/core/Property', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservablePropertyConstraint', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/isObservedByDomainConstraint', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#targetSubjectsOf'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/isObservedByRangeConstraint', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#targetObjectsOf'), ('https://astrea.linkeddata.es/shapes#2e176f370fbcb9f8e355fc1d59648bac', 'https://saref.etsi.org/core/isObservedBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#89b5017e76a20bfaef9c023845f326cc', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#b0e4858dd6a7fdf0deca7b1a3e325357', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#da754087eed62edd76c7a6cfbc9e3505', 'http://www.w3.org/ns/sosa/isObservedBy', 'http://www.w3.org/ns/shacl#path')),(('https://astrea.linkeddata.es/shapes#378884c9a8a498df70f2e193093df0af', 'http://www.w3.org/ns/ssn/System', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#cf180136b531f312cfe6d5a8998b157f', 'https://saref.etsi.org/saref4syst/System', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ActuatablePropertyConstraint', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/isActedOnByDomainConstraint', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#targetSubjectsOf'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/isActedOnByRangeConstraint', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#targetObjectsOf'), ('https://astrea.linkeddata.es/shapes#57a8c41bff032939733d67bf16e7e326', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#7bf5a93636f246b0b32724c78dace32f', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#ae7455c53047a30847be351138ab32fd', 'https://saref.etsi.org/core/isActedUponBy', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#f498e6e72b5ba7a918e1b75b9d97ab60', 'http://www.w3.org/ns/sosa/isActedOnBy', 'http://www.w3.org/ns/shacl#path')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/SensorConstraint', 'http://www.w3.org/ns/sosa/Sensor', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#d7d1e157a10d4c711970040956ced0eb', 'https://saref.etsi.org/core/Sensor', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#eef4e9102f8c4e433815a9af41e4f720', 'http://www.w3.org/ns/sosa/Sensor', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ActuationConstraint', 'http://www.w3.org/ns/sosa/Actuation', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#4a0fe07d77e1568c9f6119967b7b3d3a', 'http://www.w3.org/ns/sosa/Actuation', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#8b6c87bc4f03bc761baf9f3299f12e6c', 'https://saref.etsi.org/core/Actuation', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservationConstraint', 'http://www.w3.org/ns/sosa/Observation', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#01880a796c2df7337b5c1375c51b5b7d', 'https://saref.etsi.org/core/Observation', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#e61935f1cc0fbdc80be67c061e1cbf71', 'http://www.w3.org/ns/sosa/Observation', 'http://www.w3.org/ns/shacl#targetClass')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/FeatureOfInterestConstraint', 'http://www.w3.org/ns/sosa/FeatureOfInterest', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#34c0f55f8f3f3c58d9cb361df2984c77', 'https://saref.etsi.org/core/FeatureOfInterest', 'http://www.w3.org/ns/shacl#targetClass'), ('https://astrea.linkeddata.es/shapes#e85f7f569c1b43b31809a79038a33ed0', 'http://www.w3.org/ns/sosa/FeatureOfInterest', 'http://www.w3.org/ns/shacl#targetClass')),(('https://astrea.linkeddata.es/shapes#1747a03e68342090168eaf0538c06be3', 'http://www.w3.org/ns/ssn/isPropertyOf', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#8661dcd9ee54db004f23ae5cc74f9889', 'https://saref.etsi.org/core/isPropertyOf', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#c28a9bfd3b99f5da1c865b551408b5fe', 'http://www.w3.org/ns/ssn/isPropertyOf', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#ee1e25d05ac997f066419ef1e479566d', 'http://www.w3.org/ns/ssn/isPropertyOf', 'http://www.w3.org/ns/shacl#path')),(('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ActuationConstraint', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservationCollectionConstraint', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/ObservationConstraint', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/phenomenonTimeDomainConstraint', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#targetSubjectsOf'), ('http://stko-kwg.geog.ucsb.ed/sosa-shacl/phenomenonTimeRangeConstraint', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#targetObjectsOf'), ('https://astrea.linkeddata.es/shapes#570e251d885fe83c81ffb787ce4307aa', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#68bedd26fd82e3f121c571cff7bb1109', 'https://saref.etsi.org/core/hasPhenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#e61935f1cc0fbdc80be67c061e1cbf71', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'), ('https://astrea.linkeddata.es/shapes#f11042142401c552b10dc2bc522d4e6a', 'http://www.w3.org/ns/sosa/phenomenonTime', 'http://www.w3.org/ns/shacl#path'))]


# result = group_axioms_by_path(axioms, aligned_paths)
result = group_axioms_by_path(axioms, aligned_paths)
for res in result:
    print(res)
    print("\n")
