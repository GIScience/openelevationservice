# -*- coding: utf-8 -*-

from openelevationservice.server.api import api_exceptions
from openelevationservice.server.utils import logger
from openelevationservice.server.api.views import main_blueprint

from flask import Flask, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
#from flask_cors import CORS
import yaml
import os
import time

log = logger.get_logger(__name__)

"""load custom settings for openelevationservice"""
basedir = os.path.abspath(os.path.dirname(__file__))
SETTINGS = yaml.safe_load(open(os.path.join(basedir, 'ops_settings.yml')))

if "TESTING" in os.environ:
    SETTINGS['provider_parameters']['table_name'] = SETTINGS['provider_parameters']['table_name'] + '_test'

db = SQLAlchemy()

def create_app(script_info=None):
    # instantiate the app
    
    app = Flask(__name__, instance_relative_config=True)

    app.config['SWAGGER'] = {
        'title': 'openelevationservice',
        "swagger_version": "2.0",
        'version': 0.1,
        'uiversion': 3
    }


    # set config
    app_settings = os.getenv('APP_SETTINGS',   'openelevationservice.server.config.ProductionConfig')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    app.register_blueprint(main_blueprint)

    Swagger(app, template_file='api/oes_post.yaml')

    if "DEVELOPMENT" in os.environ:
        @app.before_request
        def before_request():
            g.start = time.time()

        @app.teardown_request
        def teardown_request(exception=None):
            # if 'start' in g:
            diff = time.time() - g.start
            logger.info("Request took: {} seconds".format(diff))

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return jsonify({"error_message": 401})

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify({"error_message": 403})

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({"error_message": 404})

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify({"error_message": 500})

    @app.errorhandler(api_exceptions.InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # shell context for flask cli
    app.shell_context_processor({
        'app': app,
        'db': db}
    )

    return app