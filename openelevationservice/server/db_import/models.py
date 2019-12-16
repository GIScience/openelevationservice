# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils import logger

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Raster

db = SQLAlchemy()

log = logger.get_logger(__name__)


class Cgiar(db.Model):
    """Database model for SRTM v4.1 aka CGIAR dataset."""

    for table in SETTINGS['provider_parameters']['tables']:

        __tablename__ = table

        rid = db.Column(db.Integer, primary_key=True)
        rast = db.Column(Raster)

        def __repr__(self):
            return '<rid {}, rast {}>'.format(self.rid, self.rast)
