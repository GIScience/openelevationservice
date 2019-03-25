# -*- coding: utf-8 -*-

from flask_testing import TestCase
from openelevationservice import TILES_DIR
from openelevationservice.server import create_app
from openelevationservice.server.db_import.models import db
from openelevationservice.server.db_import import filestreams

from os import path

app = create_app()


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('openelevationservice.server.config.TestingConfig')
        app.config['TESTING'] = True

        return app

    def setUp(self):            
        db.create_all()
        # Imports Sicily as raster, rather low-weight
        if not path.exists(path.join(TILES_DIR, 'srtm_39_05.tif')):
            test_range = [[39,40],[5,6]]
            filestreams.downloadsrtm(test_range)
        filestreams.raster2pgsql()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
