# -*- coding: utf-8 -*-
import sys


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

if sys.version_info <= (3, 5):
  error = 'Requires Python Version 3.6 or above... exiting.'
  print >> sys.stderr, error
  sys.exit(1)

setup(name='openelevationservice',
      version='0.1',
      description='Flask app to serve elevation data to GeoJSON queries.',
      long_description=readme(),
      classifiers=[
              'Development Status :: 4 - Beta',
              'License :: OSI Approved :: MIT License',
              'Operating System :: OS Independent',
              'Programming Language :: Python :: 3.7',
              ],
      keywords='flask elevation GIS GeoJSON ORS SRTM',
      url='https://github.com/GIScience/openelevationservice',
      author='Nils Nolde',
      author_email='nils.nolde@gmail.com',
      license='MIT',
      packages=['openelevationservice'],
      install_requires = [
              'flask',],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False,
      project_urls={
        'Bug Reports': 'https://github.com/GIScience/openelevationservice/issues',
        'Source': 'https://github.com/GIScience/openelevationservice',
      },)
