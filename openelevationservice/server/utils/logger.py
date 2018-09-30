# -*- coding: utf-8 -*-

import os
import logging

def get_logger(name):
    log_format = '\n%(asctime)s  %(name)8s  %(levelname)5s:  %(message)s'
    log_path = os.getenv('LOG_PATH', './')
    logging.basicConfig(format=log_format,
                        level=logging.DEBUG,
                        filename=os.path.join(os.getcwd(), 'oes_dev_log.log'),
                        filemode='w'
                       )
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)