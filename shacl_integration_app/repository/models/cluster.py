from dataclasses import dataclass, field
from .axiom import Axiom
import uuid


@dataclass
class Cluster:
    concept: str
    concept_list : list[str]
    id: str = field(init=False, default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return f"concept: {self.concept}, concept_list: {self.concept_list}, id: {self.id}"
    
@dataclass
class ConceptCluster(Cluster):
    node_axiom_cluster_list: list[Cluster]
    property_axiom_cluster_list: list[Cluster]

    def __str__(self) -> str:
        return f"{super().__str__()}, node_axiom_cluster_list: {self.node_axiom_cluster_list}, property_axiom_cluster_list: {self.property_axiom_cluster_list}"
    
@dataclass
class NodeAxiomCluster(Cluster):
    axiom_list: list[Axiom]

    def __str__(self) -> str:
        return f"{super().__str__()}, node_axiom_list: {self.axiom_list}"
    
@dataclass
class PropertyCluster(Cluster):
    property_axiom_cluster_list: list[Cluster]

    def __str__(self) -> str:
        return f"{super().__str__()}, property_axiom_list: {self.axiom_list}"
    
@dataclass
class PropertyAxiomCluster(Cluster):
    axiom_list: list[Axiom]

    def __str__(self) -> str:
        return f"{super().__str__()}, property_axiom_list: {self.axiom_list}"