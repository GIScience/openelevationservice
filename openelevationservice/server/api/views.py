# -*- coding: utf-8 -*-

from openelevationservice.server.api import api_exceptions

from flask import Blueprint, request, jsonify, Response
from voluptuous import Schema, Required, Length, Range, Coerce, Any, All, MultipleInvalid, ALLOW_EXTRA, Invalid, \
    Optional, Boolean
import copy
    
main_blueprint = Blueprint('main', __name__, )

schema = Schema({
    Required('request'): Required('geometry',
                                  msg='pois, stats or list missing'),
})    

@main_blueprint.route('/elevation', methods=['POST'])
def elevation():
    """
    Function called when user posts to /elevation.

    :returns: elevation response 
    :type: string
    """

    if request.method == 'POST':

        if 'application/json' in request.headers['Content-Type'] and request.is_json:

            all_args = request.get_json(silent=True)

            raw_request = copy.deepcopy(all_args)

            if all_args is None:
                raise api_exceptions.InvalidUsage(status_code=500, error_code=4000)

            try:
                schema(all_args)
            except MultipleInvalid as error:
                raise api_exceptions.InvalidUsage(status_code=500, error_code=4000, message=str(error))
            # query stats

    else:

        raise api_exceptions.InvalidUsage(status_code=500, error_code=4006)