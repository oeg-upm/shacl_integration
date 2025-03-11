from repository.models.cluster import Cluster

class IntegrationMethod:
    def __init__(self, input_tuples : dict, integration_option: str) -> None:
        self.input_tuples : dict = input_tuples
        self.integration_option: str = integration_option
        self.concept_clusters: list[Cluster] = None

    