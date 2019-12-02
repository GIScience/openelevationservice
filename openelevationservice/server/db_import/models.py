# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils import logger

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from geoalchemy2 import Raster

db = SQLAlchemy()

log = logger.get_logger(__name__)
table_name_terrestrial = SETTINGS['provider_parameters']['table_name_terrestrial']
table_name_bathymetry = SETTINGS['provider_parameters']['table_name_bathymetry']


class Cgiar(db.Model):
    """Database model for SRTM v4.1 aka CGIAR dataset."""

    __tablename__ = table_name_terrestrial

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)

    def __repr__(self):
        return '<rid {}, rast {}>'.format(self.rid, self.rast)


class Joerd(db.Model):
    """Database model for SRTM v4.1 aka CGIAR dataset."""

    __tablename__ = table_name_bathymetry

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)

    def __repr__(self):
        return '<rid {}, rast {}>'.format(self.rid, self.rast)
