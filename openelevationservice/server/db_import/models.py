# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils import logger

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Raster

db = SQLAlchemy()

log = logger.get_logger(__name__)


class Terrestrial(db.Model):
    """Database model for SRTM v4.1 aka CGIAR and GMTED dataset."""

    __tablename__ = list(SETTINGS['provider_parameters']['tables'].keys())[0]

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)

    def __repr__(self):
        return '<rid {}, rast {}>'.format(self.rid, self.rast)


try:
    # creates more tables if defined in ops_settings.yml
    class Bathymetry(db.Model):
        """Database model for Etopo1 dataset."""

        __tablename__ = list(SETTINGS['provider_parameters']['tables'].keys())[1]

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)
except:
    pass


try:
    # creates more tables if defined in ops_settings.yml
    class At(db.Model):
        """Database model for austrian government dataset."""

        __tablename__ = list(SETTINGS['provider_parameters']['tables'].keys())[2]

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)
except:
    pass
