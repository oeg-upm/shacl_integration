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

    # Iterate over axioms to obtain the mapping of links to paths
    for axiom in axioms:
        if axiom.pred.endswith("#path"):
            path_to_link[axiom.link].append(axiom.obj)
            link_to_paths[axiom.obj].add(axiom.link)

    # Mapping of aligned paths
    aligned_map = {}
    for paths_group in aligned_paths:
        unified_paths = set()
        for _, path_value, path_type in paths_group:
            if path_type == "http://www.w3.org/ns/shacl#path":
                unified_paths.add(path_value)
        for path in unified_paths:
            aligned_map[path] = unified_paths

        # Save in the global dictionary only when an aligned_path is found
        if unified_paths:
            global_aligned_properties_res[hashlib.sha1("".join(list(unified_paths)).encode("utf-8")).hexdigest()] = {
                "aligned_path": unified_paths
            }

    # Group axioms according to aligned paths
    for axiom in axioms:
        if axiom.link in path_to_link and not axiom.pred.endswith("#path"):
            paths = set(path_to_link[axiom.link])
            aligned_paths_set = set()
            for path in paths:
                # Check if the path is aligned
                aligned_paths_set.update(aligned_map.get(path, set()))

            # Only group if there are aligned paths
            if aligned_paths_set:
                grouped_axioms[tuple(sorted(aligned_paths_set))][axiom.pred].append(axiom.obj)
            else:
                # If not aligned, do not group
                grouped_axioms[tuple(sorted(paths))][axiom.pred].append(axiom.obj)

    # Function to determine the predominant logical operator
    def get_predominant_operator(operators):
        precedence = {"or": 1, "and": 2, "not": 3, "xone": 4}
        max_precedence = float("inf")
        predominant = None
        for op in operators:
            if op != None:
                op_precedence = precedence.get(op, float("inf"))
                if op_precedence < max_precedence:
                    max_precedence = op_precedence
                    predominant = op
            else:
                predominant = 'None'
        return predominant

    # Form the result with the necessary keys
    result = []
    for path, predicates in grouped_axioms.items():
        group = {"path": list(path), "axioms": []}

        # Get all logical operators in the group's axioms
        operators = set()
        for pred, objs in predicates.items():
            for obj in objs:
                for axiom in axioms:
                    if axiom.pred == pred and axiom.obj == obj:
                        operators.add(axiom.logical_operator)

        # Determine the predominant logical operator
        logical_operator = get_predominant_operator(operators)
        if logical_operator:
            group["logical_operator"] = logical_operator

        # Add axioms to the group
        for pred, objs in predicates.items():
            group["axioms"].append({"predicate": pred, "objects": objs})

        # Create PropertyCluster even if it is not found in the global dictionary
        property_cluster = PropertyCluster(
            property_axiom_cluster_list=[group],
            concept_list=list(path),
        )

        # If we find a match in the global dictionary, assign the id
        for cluster_id, cluster_info in global_aligned_properties_res.items():
            if set(path).issubset(cluster_info["aligned_path"]):
                property_cluster.id = cluster_id  # Assign the id from the global dictionary
                break  # If we already found the id, no need to keep searching

        # Add the PropertyCluster to the result
        result.append(property_cluster)

    return result

# Ejemplo de uso
axioms = [
    Axiom("http://www.w3.org/ns/shacl#path", "http://www.w3.org/ns/sosa/hasResult", "or", "n6879eefd7f814301873fdeb6c63905b7b7"),
    Axiom("http://www.w3.org/ns/shacl#minCount", "1", "or", "n6879eefd7f814301873fdeb6c63905b7b7"),
    Axiom("http://www.w3.org/ns/shacl#maxCount", "1", "or", "n6879eefd7f814301873fdeb6c63905b7b7"),
    Axiom("http://www.w3.org/ns/shacl#class", "http://www.w3.org/ns/sosa/Result", "or", "n6879eefd7f814301873fdeb6c63905b7b7"),
    Axiom("http://www.w3.org/ns/shacl#path", "http://www.w3.org/ns/sosa/hasSimpleResult", "and", "n6879eefd7f814301873fdeb6c63905b7b8"),
    Axiom("http://www.w3.org/ns/shacl#minCount", "1", "and", "n6879eefd7f814301873fdeb6c63905b7b8"),
    Axiom("http://www.w3.org/ns/shacl#maxCount", "1", "and", "n6879eefd7f814301873fdeb6c63905b7b8"),
    Axiom("http://www.w3.org/ns/shacl#path", "http://www.w3.org/ns/sosa/Holiwi", "and", "1243213432153465436"),
    Axiom("http://www.w3.org/ns/shacl#minCount", "1", "and", "1243213432153465436"),
    Axiom("http://www.w3.org/ns/shacl#maxCount", "1", "and", "1243213432153465436"),
]

aligned_paths = [
    (("http://example.com/alignment", "http://www.w3.org/ns/sosa/hasResult", "http://www.w3.org/ns/shacl#path"),
     ("http://example.com/alignment", "http://www.w3.org/ns/sosa/hasSimpleResult", "http://www.w3.org/ns/shacl#path"))
]

result = group_axioms_by_path(axioms, aligned_paths)
for res in result:
    print(res)
