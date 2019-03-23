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

setup(
    name='openelevationservice',
    version='0.2',
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
    install_requires=[
        'Flask>=1.0.0',
        'Flask_Cors>=3.0.0',
        'Flask-SQLAlchemy>=2.3.0',
        'Cerberus>=1.2',
        'beautifulsoup4>=4.6.0',
        'GeoAlchemy2>=0.5.0',
        'geojson>=2.4.0',
        'shapely>=1.6.0',
        'sqlalchemy>=1.2.0',
        'werkzeug>=0.14.0',
        'pyyaml>=4.2b1',
        'flasgger>=0.9.0',
        'gunicorn>=19.0.0',
        'gevent>=1.3.0',
        'requests>=2.20.0',
        'psycopg2>2.7.5'
    ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=[
        'nose>1.3.0',
        'Flask_Testing>=0.7.0',
    ],
    zip_safe=False,
    project_urls={
    'Bug Reports': 'https://github.com/GIScience/openelevationservice/issues',
    'Source': 'https://github.com/GIScience/openelevationservice',
      }
)