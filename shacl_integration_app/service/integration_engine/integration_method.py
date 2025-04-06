from shacl_integration_app.repository.models import Cluster
from shacl_integration_app.service.integration_engine.identification import Identification
from shacl_integration_app.service.integration_engine.integration import Integration
from shacl_integration_app.repository.wrappers import get_time
#from shacl_integration_app.repository.constants.constants_examples import IDENTIFICATION_CONSTANT_RESULT_EXAMPLE

class IntegrationMethod:
    def __init__(self, input_tuples : list[tuple[str, str]], integration_option: str, alignment_reference: str) -> None:
        self.input_tuples : list[tuple[str, str]] = input_tuples
        self.integration_option: str = integration_option
        self.concept_clusters: list[Cluster] = []
        self.alignment_reference: str = alignment_reference

    @get_time
    def execute_identification(self) -> list[Cluster]:
        identification_activity: Identification = Identification(input_tuples=self.input_tuples, alignment_reference=self.alignment_reference) 
        self.concept_clusters = identification_activity.execute_identification()
        return self.concept_clusters

    @get_time
    def execute_integration(self) -> dict:
        if self.concept_clusters == []:
            result: dict = {
                'error' : 'No clusters identified, therefore no integration can be performed.'
            }
        else:
            integration_activity: Integration = Integration(concept_clusters=self.concept_clusters, integration_option=self.integration_option, input_shapes_path=[tup[1] for tup in self.input_tuples])
            result: dict = integration_activity.execute_integration()

        return result
    
    @get_time
    def execute(self) -> dict:
        self.execute_identification()
        # self.concept_clusters = IDENTIFICATION_CONSTANT_RESULT_EXAMPLE
        return self.execute_integration()