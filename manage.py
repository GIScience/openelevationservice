# -*- coding: utf-8 -*-

from openelevationservice.server import create_app
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.config import SETTINGS
from openelevationservice.server.db_import.models import db
from openelevationservice.server.db_import import filestreams

log = get_logger(__name__)

app = create_app()


@app.cli.command()
def prepare():
    """Downloads SRTM tiles to disk. Can be specified over extent values in ops_settings.yml"""

    filestreams.download()
    log.info("Downloaded all files")


@app.cli.command()
def merge():
    """Merges downloaded single SRTM and GMTED tiles to one raster"""

    filestreams.merge_data()
    log.info("Merged downloaded files")
    

@app.cli.command()
def create():
    """Creates all tables defined in models.py"""
    
    db.create_all()
    for table in SETTINGS['provider_parameters']['tables']:
        log.info("Table {} was created.".format(table))
    
    
@app.cli.command()
def drop():
    """Drops all tables defined in models.py"""
    
    db.drop_all()
    for table in SETTINGS['provider_parameters']['tables']:
        log.info("Table {} was dropped.".format(table))


@app.cli.command()
def importdata(): 
    """Imports all data found in ./tiles"""

    log.info("Starting to import data...")
    filestreams.raster2pgsql()
    log.info("Imported data successfully!")
