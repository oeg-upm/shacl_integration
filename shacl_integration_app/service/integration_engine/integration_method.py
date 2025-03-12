from shacl_integration_app.repository.models import Cluster
from shacl_integration_app.service.integration_engine.identification import Identification
from shacl_integration_app.repository.wrappers import get_time

class IntegrationMethod:
    def __init__(self, input_tuples : list[tuple[str, str]], integration_option: str, alignment_reference: str) -> None:
        self.input_tuples : list[tuple[str, str]] = input_tuples
        self.integration_option: str = integration_option
        self.concept_clusters: list[Cluster] = []
        self.alignment_reference: str = alignment_reference

    @get_time
    def execute_identification(self) -> list[Cluster]:        
        # print(self.input_tuples)
        # print(self.integration_option)
        identification_activity: Identification = Identification(input_tuples=self.input_tuples, alignment_reference=self.alignment_reference) 
        self.concept_clusters = identification_activity.execute_identification()
        return self.concept_clusters

    @get_time
    def execute_integration(self) -> dict:
        # print(self.concept_clusters)
        # print(self.integration_option)
        integrated_shape_path: str = 'shape/path' # write on file
        inconsistence_report_path: str = 'report/path' # write on file
        result: dict = {
            'integrated_shape_path' : integrated_shape_path,
            'inconsistence_report_path' : inconsistence_report_path
        }

        # result: dict = {
        #     'error' : 'Error during integration'
        # }

        return result
    
    @get_time
    def execute(self) -> dict:
        self.execute_identification()
        #print(self.concept_clusters)
        return self.execute_integration()