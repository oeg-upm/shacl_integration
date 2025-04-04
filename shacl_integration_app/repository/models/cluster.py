from dataclasses import dataclass, field
from .axiom import Axiom
import uuid
import hashlib


@dataclass
class Cluster:
    concept: str = "default_cluster"
    concept_list : list[str] = field(default_factory=list)
    id: str = ''# CHANGE TO field(init=False) # CHANGE FOR EXAMPLE OF INTEGRATION TO ''

    def __post_init__(self):
        if self.concept != "default_cluster":
            self.id = hashlib.sha1(self.concept.encode("utf-8")).hexdigest()
        elif self.concept_list is not []:
            self.id = hashlib.sha1("".join(self.concept_list).encode("utf-8")).hexdigest()
        else:
            self.id = str(uuid.uuid4())

    def __str__(self) -> str:
        return f"concept: {self.concept}, concept_list: {self.concept_list}, id: {self.id}"
    
@dataclass
class ConceptCluster(Cluster):
    node_axiom_cluster_list: list[Cluster] = field(default_factory=list)
    property_cluster_list: list[Cluster] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{super().__str__()}, node_axiom_cluster_list: {self.node_axiom_cluster_list}, property_axiom_cluster_list: {self.property_cluster_list}"
    
@dataclass
class NodeAxiomCluster(Cluster):
    axiom_list: list[dict] = field(default_factory=list)
    

    def __str__(self) -> str:
        return f"{super().__str__()}, node_axiom_list: {self.axiom_list}"
    
@dataclass
class PropertyCluster(Cluster):
    property_axiom_cluster_list: list[Cluster] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{super().__str__()}, property_axiom_list: {self.property_axiom_cluster_list}"
    
@dataclass
class PropertyAxiomCluster(Cluster):
    axiom_list: dict[list[Axiom]] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{super().__str__()}, property_axiom_list: {self.axiom_list}"