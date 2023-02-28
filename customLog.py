#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Manage log and trace
'''

import logging
import os

from pathlib import Path

__author__ = "Serge LASSABE"
__copyright__ = "Copyright (C) 2023, Serge LASSABE"
__license__ = "agpl-3.0"
__version__ = "5.0.1"

class CustomFormatter(logging.Formatter):
    """Custom formatter, overrides funcName with value of name_override if it exists"""

    def format(self, record):
        if hasattr(record, 'name_override'):
            record.funcName = record.name_override
        if hasattr(record, 'file_override'):
            record.filename = record.file_override
        if hasattr(record, 'line_override'):
            record.lineno = record.line_override
        return super(CustomFormatter, self).format(record)

_DEFAULT_LOG = None

def init_log(module_name, log_name, debug=False):
    ''' Initiate loggers

    :param module_name: the moduke name with a hierarchy notation, eg domotic.storaged
    :param log_name:    the name of the file
    :param debug:       set log level to DEBUG
    :return: the logger newly created
  '''
 
    global _DEFAULT_LOG
    root_dir = Path(__file__).parent.absolute()
    log_path = os.path.join(root_dir, "log", log_name)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    # set mode='w' to clean the log file or mode='a' to append
    fh = logging.FileHandler(log_path, mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(CustomFormatter(
        '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)s - %(funcName)s : %(message)s'))
    ch.setFormatter(CustomFormatter(
        '%(filename)s:%(lineno)s - %(funcName)s : %(message)s'))

    logger.addHandler(ch)
    logger.addHandler(fh)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    _DEFAULT_LOG = logger
    return logger

def get_default_logger():
    return _DEFAULT_LOG
