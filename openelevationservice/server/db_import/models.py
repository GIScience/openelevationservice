# -*- coding: utf-8 -*-

from openelevationservice.server import db, SETTINGS
from openelevationservice.server.utils import logger

from geoalchemy2 import Raster

log = logger.get_logger(__name__)

class Cgiar(db.Model):
    __tablename__ = SETTINGS['provider_parameters']['table_name']
    log.info("Table {} was created.".format(__tablename__))
    
    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)