# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS
from openelevationservice.server.sources import PROVIDER_MAPPING
from openelevationservice.server.utils.logger import get_logger

from os import path, environ
import subprocess

log = get_logger(__name__)

# TODO: write Exception


def download():
    """Selects download provider."""

    extent_settings = SETTINGS['tables']['terrestrial']['extent']
    download_list = []

    if SETTINGS['provider_parameters']['tables']['terrestrial']:

        # only SRTM data download
        if 60 >= extent_settings['max_y'] >= -60:
            provider = PROVIDER_MAPPING['terrestrial']['srtm']()
            download_list.append(provider)

        # SRTM and GMTED data download
        elif extent_settings['max_y'] > 60 >= extent_settings['min_y'] or \
                extent_settings['max_y'] > -60 >= extent_settings['min_y']:
            for source in SETTINGS['tables']['terrestrial']['sources']:
                provider = PROVIDER_MAPPING['terrestrial'][source]()
                download_list.append(provider)

        # only GMTED data download
        else:
            provider = PROVIDER_MAPPING['terrestrial']['gmted']()
            download_list.append(provider)

    if SETTINGS['provider_parameters']['tables']['bathymetry']:
        provider = PROVIDER_MAPPING['etopo1']()
        download_list.append(provider)

    if SETTINGS['provider_parameters']['tables']['at']:
        provider = PROVIDER_MAPPING['gv_at']()
        download_list.append(provider)

    for download_provider in download_list:
        try:
            download_provider.download_data()
        except Exception as err:
            log.error(err)


def merge_data():
    """Selects provider for further raster tile resampling and merging."""

    extent_settings = SETTINGS['tables']['terrestrial']['extent']
    merge_list = []

    if SETTINGS['provider_parameters']['tables']['terrestrial']:
        # only SRTM data
        if 60 >= extent_settings['max_y'] >= -60:
            provider = PROVIDER_MAPPING['terrestrial']['srtm']()
            merge_list.append(provider)

        # GMTED data or GMTED and SRTM data
        elif extent_settings['max_y'] > 60 or extent_settings['min_y'] < -60:
            provider = PROVIDER_MAPPING['terrestrial']['gmted']()
            merge_list.append(provider)

    if SETTINGS['provider_parameters']['tables']['bathymetry']:
        provider = PROVIDER_MAPPING['etopo1']()
        merge_list.append(provider)

    if SETTINGS['provider_parameters']['tables']['at']:
        provider = PROVIDER_MAPPING['gv_at']()
        merge_list.append(provider)

    for merge_provider in merge_list:
        try:
            merge_provider.merge_tiles()
        except Exception as err:
            log.error(err)


def raster2pgsql():
    """
    Imports SRTM v4.1 tiles to PostGIS.
    
    :raises subprocess.CalledProcessError: Raised when raster2pgsql throws an error.
    """

    # TODO: define -t spatial size
    # TODO: bathy_raster.tif -> just one row?
    # TODO: import single files, too?
    pg_settings = SETTINGS['provider_parameters']

    # Copy all env variables and add PGPASSWORD
    env_current = environ.copy()
    env_current['PGPASSWORD'] = pg_settings['password']

    for table in SETTINGS['provider_parameters']['tables'].items():
        if table[1] is not None:
            filename = path.join(TILES_DIR + '/' + table[0] + '_raster.tif')

            # Tried to import every raster individually by user-specified xyrange
            # similar to download(), but raster2pgsql fuck it up somehow.. The PostGIS
            # raster will not be what one would expect. Instead doing a bulk import of all files.
            cmd_raster2pgsql = r"raster2pgsql -s 4326 -a -C -M -t 50x50 {filename} {table_name} | psql -q -h {host} -p {port} -U {user_name} -d {db_name}"
            # -s: raster SRID
            # -a: append to table (assumes it's been create with 'create()')
            # -C: apply all raster Constraints
            # -M: vacuum analyze after import
            # -t: specifies the pixel size of each row. Important to keep low for performance!

            cmd_raster2pgsql = cmd_raster2pgsql.format(**{'filename': filename, 'table_name': table[1], **pg_settings})

            proc = subprocess.Popen(cmd_raster2pgsql,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=True,
                                    env=env_current)

            return_code = proc.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, cmd_raster2pgsql)
