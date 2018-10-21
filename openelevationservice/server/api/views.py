# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.api import api_exceptions
from openelevationservice.server.utils import logger, convert
from openelevationservice.server.api import querybuilder
from openelevationservice.server.api.response import ResponseBuilder

from shapely import wkt
from flask import Blueprint, request, jsonify
from voluptuous import Schema, Required, Any, Optional, REMOVE_EXTRA, MultipleInvalid
    
log = logger.get_logger(__name__)

main_blueprint = Blueprint('main', __name__, )

@main_blueprint.route('/elevation/line', methods=['POST'])
def elevationline():
    """
    Function called when user posts to /elevation/line.

    :returns: elevation response 
    :type: Response
    """
    
    _validate_request(request)
    
    req_args = request.get_json(silent=True)
    
    # Check incoming parameters
    geometry_str = req_args['geometry']
    format_in = req_args['format_in']
    if 'format_out' not in req_args:
        req_args['format_out'] = 'geojson'
    format_out = req_args['format_out']
      
    # Get the geometry
    if format_in == 'geojson':
        geom = convert.geojson_to_geometry(geometry_str)
    elif format_in == 'encodedpolyline':
        geom = convert.decode_polyline(geometry_str)
    elif format_in == 'linestring':
        geom = convert.polyline_to_geometry(geometry_str)
        
    if len(list(geom.coords)) > SETTINGS['maximum_nodes']:
        raise api_exceptions.InvalidUsage(status_code=500,
                                          error_code=4003,
                                          message='Maximum number of nodes exceeded.')
                
    results = ResponseBuilder().__dict__
    results['geometry'] = querybuilder.line_elevation(geom, format_out)
    
    # decision tree for format_out
    if format_out != 'geojson':
        geom_out = wkt.loads(results['geometry'])
        coords = geom_out.coords
        if format_out == 'encodedpolyline':
            results['geometry'] = convert.encode_polyline(coords, True)
        else:
            results['geometry'] = list(coords)
    
    return jsonify(results)


@main_blueprint.route('/elevation/point', methods=['POST', 'GET'])
def elevationpoint():
    """
    Function called when user posts to/gets /elevation/point.

    :returns: elevation response 
    :type: Response class
    """
    
    _validate_request(request)
    
    if request.method == 'POST':
        req_args = request.get_json(silent=True)
        
        # Check incoming parameters
        req_geometry = req_args['geometry']
        format_in = req_args['format_in']
        if 'format_out' not in req_args:
            req_args['format_out'] = 'geojson'
        format_out = req_args['format_out']
            
        # Get the geometry
        if format_in == 'geojson':
            geom = convert.geojson_to_geometry(req_geometry)
        if format_in == 'point':
            geom = convert.point_to_geometry(req_geometry)
    else:
        # If request method is GET
        # Coercing request ImmutableMultiDict to dict() makes the values lists,
        # so we have to access the first elements
        req_args = dict(request.args)
        
        req_geometry = req_args['geometry'][0]
        if 'format_out' not in req_args:
            req_args['format_out'] = ['geojson']
        format_out = req_args['format_out'][0]
        try:
            # Catch errors when parsing the input string
            point_coords = [float(x) for x in req_geometry.split(',')]
        except:
            raise api_exceptions.InvalidUsage(500,
                                              4000,
                                              '{} is not a comma separated list of long, lat'.format(req_geometry))

        geom = convert.point_to_geometry(point_coords)
    
    # Build response with attribution etc.
    results = ResponseBuilder().__dict__
    results['geometry'] = querybuilder.point_elevation(geom, format_out)
    
    if format_out != 'geojson':
        geom_out = wkt.loads(results['geometry'])
        results['geometry'] = list(geom_out.coords[0])

    return jsonify(results)
            

schema_post = Schema({Required('geometry'): Required(Any(object, list, str)),
                     Required('format_in'): Required(Any('geojson',
                                                     'point',
                                                     'encodedpolyline',
                                                     'linestring')),
                    Optional('format_out'): Required(Any('geojson',
                                                     'point',
                                                     'encodedpolyline',
                                                     'linestring'))
                     })

# The schema looks so weird, bcs request.args is ImmutableMultiDict, which
# has listed values when coerced to dict()                     
schema_get = Schema({Required('geometry'): str,
                     Optional('format_out'): Required(Any('geojson', 'point'))}, extra=REMOVE_EXTRA)

def _validate_request(request):
    """
    Validates for emptiness and application/json in header
    
    :param request: POST or GET request from user
    :type request: Flask request
    """        
    
    try:
        if request.method == 'GET':
            schema_get(request.args.to_dict())
        
        if request.method == 'POST':
            if not 'application/json' in request.headers['Content-Type']:
                log.debug(request.headers)
                raise api_exceptions.InvalidUsage(500, 
                                                  4001,
                                                  "Content-Type header is not application/json")
            schema_post(request.get_json())   
    except MultipleInvalid as e:
        raise api_exceptions.InvalidUsage(500,
                                          4000,
                                          str(e))

    
