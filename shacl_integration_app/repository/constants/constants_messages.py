# OK messages

MESSAGE_INTEGRATION_OK: dict = (lambda id, operation, integrated_shape_path, inconsistences_report_path : {
    "message": f'Integration of shapes with id: [{id}], using operation: [{operation}]',
    "status": "OK",
    "integrated_shape": f'{integrated_shape_path}',
    "inconsistences_report": f'{inconsistences_report_path}'
    })

# KO messages

MESSAGE_INTEGRATION_INVALID_OPERATION_KO: str = 'Invalid operation, please use either \"union\" or \"intersection\"'
MESSAGE_INTEGRATION_INVALID_ID_KO: str = (lambda json_data : f'Invalid id, please use one of the following: {", ".join([f"[{str(key)}]" for key in json_data.keys()])}')
MESSAGE_INTEGRATION_KO: dict = (lambda id, operation, error_message : {
    "message": f'Integration of shapes with id: [{id}], using operation: [{operation}]',
    "status": "ERROR",
    "error": f'{error_message}'
    })




# IMPORT CODE
__all__ = [*locals().keys()]