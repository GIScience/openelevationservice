# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils import logger

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Raster

db = SQLAlchemy()

log = logger.get_logger(__name__)


if SETTINGS['provider_parameters']['tables']['terrestrial']:
    class Terrestrial(db.Model):
        """Database model for SRTM v4.1 aka CGIAR and GMTED dataset."""

        __tablename__ = SETTINGS['provider_parameters']['tables']['terrestrial']

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)


if SETTINGS['provider_parameters']['tables']['bathymetry']:
    class Bathymetry(db.Model):
        """Database model for Etopo1 dataset."""

        __tablename__ = SETTINGS['provider_parameters']['tables']['bathymetry']

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)


if SETTINGS['provider_parameters']['tables']['at']:
    class At(db.Model):
        """Database model for austrian government dataset."""

        __tablename__ = SETTINGS['provider_parameters']['tables']['at']

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)
