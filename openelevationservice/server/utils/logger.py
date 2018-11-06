# -*- coding: utf-8 -*-

import os
import logging

def get_logger(name):
    """
    Instantiate a logger with a defined name, e.g. module name.
    
    :param name: name for the logger
    :type name: string
    
    :returns: a logger object
    :rtype: logging.Logger
    """
    
    log_format = '\n%(asctime)s  %(name)8s  %(levelname)5s:  %(message)s'
    log_level = os.getenv('OES_LOGLEVEL', 'INFO')
    logging.basicConfig(format=log_format,
                        level=log_level
                       )
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)