# -*- coding: utf-8 -*-

import os
import logging

def get_logger(name):
    log_format = '\n%(asctime)s  %(name)8s  %(levelname)5s:  %(message)s'
    log_path = os.getenv('LOG_PATH', './')
    logging.basicConfig(format=log_format,
                       )
    console = logging.StreamHandler()
#    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)