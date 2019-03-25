# -*- coding: utf-8 -*-

from openelevationservice.server.api import api_exceptions
from openelevationservice.server.utils import logger

from cerberus import Validator, TypeDefinition

log = logger.get_logger(__name__)

object_type = TypeDefinition("object", (object,), ())
Validator.types_mapping['object'] = object_type
v = Validator()

schema_post = {'geometry': {'anyof_type': ['object', 'list', 'string'], 'required': True},
               'format_in': {'type': 'string', 'allowed': ['geojson', 'point', 'encodedpolyline', 'encodedpolyline5', 'encodedpolyline6', 'polyline'], 'required': True},
               'format_out': {'type': 'string', 'allowed': ['geojson', 'point', 'encodedpolyline', 'encodedpolyline5', 'encodedpolyline6', 'polyline'], 'default': 'geojson'},
               'dataset': {'type': 'string', 'allowed': ['srtm'], 'default': 'srtm'}
               }

schema_get = {'geometry': {'type': 'string', 'required': True},
              'format_out': {'type': 'string', 'allowed': ['geojson', 'point'], 'default': 'geojson'},
              'dataset': {'type': 'string', 'allowed': ['srtm'], 'default': 'srtm'}
              }

def validate_request(request):
    """
    Validates full request with regards to validation schemas and HTTP headers.
    
    :param request: POST or GET request from user
    :type request: Flask request
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.
    
    :returns: validated and normalized request arguments
    :rtype: dict
    """        
    if request.method == 'GET':
        v.allow_unknown = True
        v.validate(dict(request.args), schema_get)
    
    if request.method == 'POST':
        if request.headers.get('Content-Type') != 'application/json':
            raise api_exceptions.InvalidUsage(500, 
                                              4001,
                                              "Content-Type header is not application/json")

        v.validate(request.get_json(), schema_post) 
        
    if v.errors:
        errors = []
        for error in v.errors:
            errors.append("Argument '{}': {}".format(error, v.errors[error][0]))
        raise api_exceptions.InvalidUsage(500,
                                          4000,
                                          ", ".join(errors))
    
    return v.document