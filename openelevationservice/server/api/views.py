# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.api import api_exceptions
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.api.querybuilder import request_elevation

from flask import Blueprint, request, Response
import geojson
from shapely.geometry import shape
    
log = get_logger(__name__)

main_blueprint = Blueprint('main', __name__, )

@main_blueprint.route('/elevation/line', methods=['POST'])
def elevation():
    """
    Function called when user posts to /elevation/line.

    :returns: elevation response 
    :type: Response
    """

    if request.method == 'POST':
        if 'application/json' in request.headers['Content-Type']:
            if request is None:
                raise api_exceptions.InvalidUsage(status_code=500,
                                                  error_code=4000,
                                                  message='Empty reques')
            # Make sure geojson is valid
            # invokes shapely's __geo_interface__ method
            try:
                geom = shape(geojson.loads(request.data))
            except Exception as e:
                raise api_exceptions.InvalidUsage(status_code=500,
                                                  error_code=4001,
                                                  message=str(e))
                
            if len(list(geom.coords)) > SETTINGS['maximum_nodes']:
                raise api_exceptions.InvalidUsage(status_code=500,
                                                  error_code=4002,
                                                  message='Maximum number of nodes exceeded.')
            
            if geom.geom_type not in ('LineString', 'Point'):
                raise api_exceptions.InvalidUsage(status_code=500,
                                                  error_code=4001,
                                                  message='GeoJSON type {} not supported'.format(geom.geom_type))
            
            results = request_elevation(geom)
            
    else:
        raise api_exceptions.InvalidUsage(status_code=500,
                                          error_code=4000,
                                          message='Unsupported method') 
    
    return Response(results, mimetype='application/json; charset=utf-8')