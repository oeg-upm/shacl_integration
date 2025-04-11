from flask import Blueprint, request, render_template
import os
import sys
import json
from shacl_integration_app.repository.constants import *
from shacl_integration_app.repository.constants import count_constants
from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster, PropertyAxiomCluster
from shacl_integration_app.repository.wrappers import get_time
from shacl_integration_app.service.integration_engine import IntegrationMethod, Identification, Integration
sys.stdout.flush()

integrate = Blueprint('integrate', __name__)


@integrate.route('/integration_options', methods=['GET'])
def integration_possibilities() -> dict:
    json_response: dict = {key: json_data[key]['description'] for key in json_data.keys()}
    return json_response


@integrate.route('/integrate/<id>/<operation>', methods=['POST'])
@get_time
def integration(id: str, operation: str) -> str:

    count_constants.global_inconsistences_counter = 0
    count_constants.global_integration_counter = 0
    # Check if the operation is valid and if the id is in the json_data
    if operation not in ['union', 'intersection']:
        return MESSAGE_INTEGRATION_INVALID_OPERATION_KO, BAD_REQUEST
    elif id not in json_data.keys():
        return MESSAGE_INTEGRATION_INVALID_ID_KO(json_data=json_data), BAD_REQUEST

    # Create input_tuples list
    input_tuples: list[tuple[str, str]] = [(key['onto'], key['shape'])for key in json_data[id]['tuples']]
    alignment_reference: str = json_data[id]['alignment_reference']

    # Execute integration
    integration: IntegrationMethod = IntegrationMethod(input_tuples=input_tuples, integration_option=operation, alignment_reference=alignment_reference)
    result: dict = integration.execute()

    print(f"Number of inconsistences: {count_constants.global_inconsistences_counter}")
    print(f"Number of integrations: {count_constants.global_integration_counter}")

    # Check if the result is valid
    if all(key in result for key in ['integrated_shape_path', 'inconsistences_report_path']):
        return MESSAGE_INTEGRATION_OK(id=id, operation=operation,
                                      integrated_shape_path=result['integrated_shape_path'],
                                      inconsistences_report_path=result['inconsistences_report_path'],
                                      inconsistences=count_constants.global_inconsistences_counter,
                                      integrations=count_constants.global_integration_counter
                                      ), OK
    else:
        return MESSAGE_INTEGRATION_KO(id=id,
                                      operation=operation,
                                      error_message=result['error']
                                    ), INTERNAL_SERVER_ERROR