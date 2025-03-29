from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster
from shacl_integration_app.repository.rule_library.filter_library import Filter_Library

class InconsistencesFilter:
    """
    Class to filter inconsistencies in the SHACL integration process.
    """
    def __init__(self, concept_clusters: list[Cluster]) -> None:
        self.concept_clusters = concept_clusters
        

    def filter_inconsistencies(self) -> list[Cluster]:
        """
        Filter inconsistencies from the SHACL data.
        """

        return self.concept_clusters