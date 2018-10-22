# -*- coding: utf-8 -*-

from openelevationservice.server import create_app
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.config import SETTINGS
from openelevationservice.server.db_import.models import db
from openelevationservice.server.db_import import filestreams

import click

log = get_logger(__name__)

app = create_app()

@app.cli.command()
@click.option('--xyrange', default='0,73,0,25')
def download(xyrange):
    """
    Downloads SRTM tiles to disk. Can be specified over minx, maxx, miny, maxy.
    
    :param xyrange: A comma-separated list of x_min, x_max, y_min, y_max
        in that order. For reference grid, see http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp
    :type xyrange: comma-separated integers
    """
    
    filestreams.downloadsrtm(_arg_format(xyrange))
    log.info("Downloaded all files")
    

@app.cli.command()
def create():
    """Creates all tables defined in models.py"""
    
    db.create_all()
    log.info("Table {} was created.".format(SETTINGS['provider_parameters']['table_name']))
    
    
@app.cli.command()
def drop():
    """Drops all tables defined in models.py"""
    
    db.drop_all()
    log.info("Table {} was dropped.".format(SETTINGS['provider_parameters']['table_name']))
    

@app.cli.command()
@click.option('--xyrange', default='0,73,0,25')
def importdata(xyrange): 
    """
    Imports all data found in ./tiles
    
    :param xyrange: A comma-separated list of x_min, x_max, y_min, y_max
        in that order. For reference grid, see http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp
    :type xyrange: comma-separated integers
    """
    log.info("Starting to import data...")
    
    filestreams.raster2pgsql(_arg_format(xyrange))
    
    log.info("Imported data successfully!")
    

def _arg_format(xy_range_txt):
    
    str_split = [int(s.strip()) for s in xy_range_txt.split(',')]
    
    xy_range = [[str_split[0], str_split[1]],
                [str_split[2], str_split[3]]]
    
    return xy_range