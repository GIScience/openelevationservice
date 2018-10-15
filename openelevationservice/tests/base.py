# -*- coding: utf-8 -*-

from flask_testing import TestCase
from flask import Flask
from openelevationservice.server import create_app
from openelevationservice.server.db_import.models import db
from openelevationservice.server.db_import import datahandler

app = create_app()

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('openelevationservice.server.config.TestingConfig')
        app.comfig['TESTING'] = True

        return app

    def setUp(self):
        db.create_all()

        test_range = [[39,40],[5,6]]
        datahandler.downloaddata(test_range)
        datahandler.raster2pgsql(test_range)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
