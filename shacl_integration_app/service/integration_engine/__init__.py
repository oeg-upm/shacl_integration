from .integration_method import IntegrationMethod
from .identification.identification import Identification
from .integration.integration import Integration

__all__ = ['IntegrationMethod', 'Identification', 'Integration']

__author__ = 'Salvador González Gerpe'
__email__ = 'salgonger1997@gmail.com'
__version__ = '0.0.1'
__date__ = '2025-03-12'
__status__ = 'development'
__doc__ = 'This module is an integration engine that follows an integration method to integrate SHACL shapes. It receives as input a dictionary of ontologies and SHACL tuples and returns as output an integrated SHACL shape together with a report of the possible inconsistencies occurred during the inconsistency filtering activity.'