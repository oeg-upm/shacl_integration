from shacl_integration_app.repository.models import Cluster
from shacl_integration_app.repository.wrappers import get_time
from shacl_integration_app.service.integration_engine.integration.inconsistences_filter import InconsistencesFilter
from shacl_integration_app.service.integration_engine.integration.integration_operation import IntegrationOperation
from rdflib import Graph
import os

class Integration:
    def __init__(self, concept_clusters: list[Cluster], integration_option: str, input_shapes_path: list[str]) -> None:
        self.concept_clusters: list[Cluster] = concept_clusters
        self.integration_option: str = integration_option
        self.common_path: str = os.path.commonpath(input_shapes_path)
        self.integrated_shacl_shape : Graph = Graph()
        
    @get_time
    def execute_integration(self) -> dict:
        """
        Execute the SHACL integration process.
        """
        # Execute SHACL inconsistences filter process
        inconsistences_report_path, concept_clusters_without_inconsistences = self.execute_inconsistences_filter()
        if 'Error' in inconsistences_report_path:
            return {
                'error': inconsistences_report_path
            }
        
        # Execute integration operation process
        concept_clusters_integrated = self.execute_integration_operation(
            concept_clusters_without_inconsistences=concept_clusters_without_inconsistences)
        if type(concept_clusters_integrated) == str and 'Error' in concept_clusters_integrated:
            return {
                'error': concept_clusters_integrated
            }
        
        # Execute SHACL unification process
        integrated_shape_path = self.execute_shacl_unification(concept_clusters_integrated=concept_clusters_integrated)
        if 'Error' in integrated_shape_path:
            return {
                'error': integrated_shape_path
            }
        
        return {
            'integrated_shape_path': integrated_shape_path,
            'inconsistences_report_path': inconsistences_report_path
        }


    @get_time
    def execute_inconsistences_filter(self) -> tuple[str, list[Cluster]] | str:
        """
        Execute the SHACL inconsistences filter process.
        """
        inconsistences_report_path:str = self.common_path + '/inconsistences_report.ttl'
        try:

            # Execute inconsistency filter process
            # input -> self.concept_clusters, inconsistences_report_path
            # output -> concept_clusters_without_inconsistences
            # concept_clusters_without_inconsistences: list[Cluster] = self.concept_clusters.copy() # TODO: update this list with the filtered clusters removing the clusters with inconsistences

            inconsistences_filter = InconsistencesFilter(concept_clusters=self.concept_clusters,
                                                         inconsistences_report_path=inconsistences_report_path,
                                                         integration_option=self.integration_option)
            concept_clusters_without_inconsistences: list[Cluster] = inconsistences_filter.filter_inconsistencies()
        
            if concept_clusters_without_inconsistences == self.concept_clusters:
                inconsistences_report_path = 'No inconsistences found within the clusters.'
                
            return inconsistences_report_path, concept_clusters_without_inconsistences # TODO: update this list with the filtered clusters removing the clusters with inconsistences
        except Exception as e:
            return (f"Error during SHACL inconsistences filter process: {e}"), []


    @get_time
    def execute_integration_operation(self, concept_clusters_without_inconsistences: list[Cluster]) -> list[Cluster] | str:
        """
        Execute the SHACL integration operation process.
        """
        # Execute integration operation process
        # input -> concept_clusters_without_inconsistences
        # output -> concept_clusters_integrated
        try:
            concept_clusters_integrated: list[Cluster] = concept_clusters_without_inconsistences.copy()
            return concept_clusters_integrated
        except Exception as e:
            return (f"Error during integration operation: {e}")
    

    @get_time
    def execute_shacl_unification(self, concept_clusters_integrated: list[Cluster]) -> str:
        """
        Execute the SHACL unification process.
        """
        
        try:
            self.integrated_shacl_shape : Graph = Graph() # TODO: remove this line later
            # Execute SHACL unification process
            # input -> final_concept_clusters
            # output -> integrated_shape_path, Graph()
            integrated_shape_path: str = self.common_path + '/integrated_shape.ttl'
            return integrated_shape_path
        except Exception as e:
            return (f"Error during SHACL unification process: {e}")

        