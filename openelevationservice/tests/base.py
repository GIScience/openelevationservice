# -*- coding: utf-8 -*-

from flask_testing import TestCase
from openelevationservice.server import create_app
from openelevationservice.server.db_import.models import db
from openelevationservice.server.db_import import filestreams

app = create_app()

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('openelevationservice.server.config.TestingConfig')
        app.config['TESTING'] = True

        return app

    def setUp(self):
        db.init_app(self.app)
        db.create_all()
        
        # Imports Sicily as raster, rather low-weight
        test_range = [[39,40],[5,6]]
#        filestreams.downloadsrtm(test_range)
        filestreams.raster2pgsql(test_range)

    def tearDown(self):
        db.session.remove()
        db.drop_all()