# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.api import api_exceptions
from openelevationservice.server.utils import logger, convert, codec
from openelevationservice.server.api import querybuilder, validator
from openelevationservice.server.api.response import ResponseBuilder

from shapely import wkt
import json
from flask import Blueprint, request, jsonify
    
log = logger.get_logger(__name__)

main_blueprint = Blueprint('main', __name__, )

@main_blueprint.route('/elevation/line', methods=['POST'])
def elevationline():
    """
    Function called when user posts to /elevation/line.
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.

    :returns: elevation response 
    :rtype: Response
    """
    # Cerberus validates and returns a processed arg dict
    req_args = validator.validate_request(request)
    
    # Incoming parameters
    geometry_str = req_args['geometry']
    format_in = req_args['format_in']
    format_out = req_args['format_out']
    dataset = req_args['dataset']
      
    # Get the geometry
    if format_in == 'geojson':
        geom = convert.geojson_to_geometry(geometry_str)
    elif format_in in ['encodedpolyline', 'encodedpolyline5']:
        geom = codec.decode(geometry_str, precision=5, is3d=False)
    elif format_in == 'encodedpolyline6':
        geom = codec.decode(geometry_str, precision=6, is3d=False)
    elif format_in == 'polyline':
        geom = convert.polyline_to_geometry(geometry_str)
    else:
        raise api_exceptions.InvalidUsage(400,
                                          4000,
                                          f'Invalid format_in value "{format_in}"')
        
    if len(list(geom.coords)) > SETTINGS['maximum_nodes']:
        raise api_exceptions.InvalidUsage(status_code=400,
                                          error_code=4003,
                                          message='Maximum number of nodes exceeded.')
                
    results = ResponseBuilder().__dict__
    geom_queried = querybuilder.line_elevation(geom, format_out, dataset)
    
    # decision tree for format_out
    if format_out != 'geojson':
        geom_out = wkt.loads(geom_queried)
        coords = geom_out.coords
        if format_out in ['encodedpolyline', 'encodedpolyline5']:
            results['geometry'] = codec.encode(coords, precision=5, is3d=True)
        elif format_out == 'encodedpolyline6':
            results['geometry'] = codec.encode(coords, precision=6, is3d=True)
        else:
            results['geometry'] = list(coords)
    elif format_out == 'geojson':
        results['geometry'] = json.loads(geom_queried)
    else:
        raise api_exceptions.InvalidUsage(400,
                                          4000,
                                          f'Invalid format_out value "{format_out}"')
    
    return jsonify(results)


@main_blueprint.route('/elevation/point', methods=['POST', 'GET'])
def elevationpoint():
    """
    Function called when user posts to/gets /elevation/point.
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.

    :returns: elevation response 
    :rtype: Response class
    """
    
    req_args = validator.validate_request(request)
    log.debug(req_args)
    
    if request.method == 'POST':

        # Check incoming parameters
        req_geometry = req_args['geometry']
        format_in = req_args['format_in']
        format_out = req_args['format_out']
        dataset = req_args['dataset']
            
        # Get the geometry
        if format_in == 'geojson':
            geom = convert.geojson_to_geometry(req_geometry)
        elif format_in == 'point':
            geom = convert.point_to_geometry(req_geometry)
        else:
            raise api_exceptions.InvalidUsage(
                400,
                4000,
                f"Invalid format_in value {format_in}"
            )
    else:
        req_geometry = req_args['geometry']
        format_out = req_args['format_out']
        dataset = req_args['dataset']
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
    geom_queried = querybuilder.point_elevation(geom, format_out, dataset)
    
    if format_out == 'point':
        geom_out = wkt.loads(geom_queried)
        results['geometry'] = list(geom_out.coords[0])
    elif format_out == 'geojson':
        results['geometry'] = json.loads(geom_queried)
    else:
        raise api_exceptions.InvalidUsage(400,
                                          4000,
                                          f'Invalid format_out value "{format_out}"')

    return jsonify(results)
