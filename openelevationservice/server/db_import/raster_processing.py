# -*- coding: utf-8 -*-

from openelevationservice import TILES_DIR, SETTINGS

from osgeo import gdal, gdalconst
import subprocess
from os import path


# TODO: if files already exists ...
# TODO: handle in memory files


def merge_raster(input_filename, output_filename, reference=None):
    """ Merge downloaded single tiles to one raster tile. """

    output_merge = path.join(TILES_DIR + output_filename)
    input_files = path.join(TILES_DIR + '/' + input_filename)

    if not path.exists(path.join(TILES_DIR, output_merge)):

        if reference is None:

            raster_merge = r"/usr/bin/gdal_merge.py -o {outfile} -of {outfile_format} {input_files}"

            cmd_merge = raster_merge.format(**{'outfile': output_merge,
                                               'outfile_format': 'GTiff',
                                               'input_files': input_files})

        else:
            # merge srtm and gmted tile fractions
            output_merge = path.join(TILES_DIR + output_filename)
            reference_file = path.join(TILES_DIR + reference)

            # -tap: align tiles
            # reference_file: In areas of overlap, the last image will be copied over earlier ones.
            merge = r"/usr/bin/gdal_merge.py -o {outfile} -of {outfile_format} -tap {input_files} {reference_file}"

            cmd_merge = merge.format(**{'outfile': output_merge,
                                        'outfile_format': 'GTiff',
                                        'input_files': input_files,  # gmted
                                        'reference_file': reference_file})  # srtm

        proc = subprocess.Popen(cmd_merge,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=True)

        return_code = proc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd_merge)


def clip_raster(merged_filename, output_filename):
    """ Clip merged raster by defined extent. """

    if not path.exists(path.join(TILES_DIR, output_filename)):

        output_clip = path.join(TILES_DIR + output_filename)
        merged_file = path.join(TILES_DIR + merged_filename)
        merged_data = gdal.Open(merged_file, gdalconst.GA_ReadOnly)

        extent = list(SETTINGS['tables'][0]['srtm']['extent'].values())

        # TODO: -t_srs {target_spatial_ref}
        srtm_clip = r"/usr/bin/gdalwarp -t_srs {target_spatial_ref} -dstnodata -9999 -te {extent} -of {outfile_format} {input_file} {out_clipped_file}"

        cmd_clip = srtm_clip.format(**{'target_spatial_ref': merged_data.GetProjection(),
                                       'extent': extent,
                                       'outfile_format': 'GTiff',
                                       'input_file': merged_file,
                                       'out_clipped_file': output_clip})

        proc_clip = subprocess.Popen(cmd_clip,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     shell=True)

        return_code_clip = proc_clip.wait()
        if return_code_clip:
            raise subprocess.CalledProcessError(return_code_clip, cmd_clip)


def gmted_resampling():
    """ Resample merged GMTED raster to SRTM resolution. """

    output_resampled = path.join(TILES_DIR + '/gmted_resampled.tif')

    if not path.exists(path.join(TILES_DIR, output_resampled)):

        gmted_merged = path.join(TILES_DIR + '/gmted_merged.tif')

        srtm_clipped = path.join(TILES_DIR + '/srtm_clipped.tif')
        reference_data = gdal.Open(srtm_clipped, gdalconst.GA_ReadOnly)
        # desired resolution
        x_res = reference_data.GetGeoTransform()[1]
        y_res = reference_data.GetGeoTransform()[5]

        extent = list(SETTINGS['tables'][0]['srtm']['extent'].values())

        # TODO: need extent?
        resampling = r"/usr/bin/gdalwarp -t_srs {target_spatial_ref} -dstnodata -9999 -te {extent} -tr {x_res} {y_res} -r {resampling_method} -of {outfile_format} {input_file} {out_resampling_file}"

        cmd_resampling = resampling.format(**{'target_spatial_ref': reference_data.GetProjection(),
                                              'extent': extent,
                                              'x_res': x_res,
                                              'y_res': y_res,
                                              'resampling_method': 'average',
                                              'outfile_format': 'GTiff',
                                              'input_file': gmted_merged,
                                              'out_resampling_file': output_resampled})

        proc_resampling = subprocess.Popen(cmd_resampling,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           shell=True)

        return_code_resampling = proc_resampling.wait()
        if return_code_resampling:
            raise subprocess.CalledProcessError(return_code_resampling, cmd_resampling)
