# -*- coding: utf-8 -*-

from openelevationservice.server.utils import logger
from flask_sqlalchemy import SQLAlchemy
from openelevationservice.server.config import SETTINGS

db = SQLAlchemy()

from geoalchemy2 import Raster

log = logger.get_logger(__name__)

class Cgiar(db.Model):
    __tablename__ = SETTINGS['provider_parameters']['table_name']
    
    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)
    filename = db.Column(db.Text)