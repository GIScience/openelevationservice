# -*- coding: utf-8 -*-

from openelevationservice.server import SETTINGS


class BaseConfig(object):
    """Base configuration."""

    # SECRET_KEY = 'my_precious'
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class ProductionConfig(BaseConfig):
    """Production configuration."""

    # SECRET_KEY = 'my_precious'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user_name}:{password}@{host}:{port}/{db_name}'.format(**SETTINGS['provider_parameters'])
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
    'pg':        'postgresql://{user_name}:{password}@{host}:{port}/{db_name}'.format(**SETTINGS['provider_parameters']), 
    }


class DevelopmentConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = 'postgresql://gis:gis@localhost:5432/gis'
    DEBUG_TB_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


#class TestingConfig(BaseConfig):
#    """Testing configuration."""
#
#    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(pg_settings['user_name'], pg_settings['password'],
#                                                                   pg_settings['host'], pg_settings['port'],
#                                                                   pg_settings['db_name'])
#    DEBUG_TB_ENABLED = False
#    PRESERVE_CONTEXT_ON_EXCEPTION = False
