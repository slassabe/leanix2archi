#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Main module : manage readers and writers conversion modules
'''

import datetime
import sys
import os
import json
from pathlib import Path
import pysftp
import requests

from leanIXConverterModels import Model
from connectorAPI import GraphQLReader
from connectorArchi import XmlArchiWriter
from connectorExcel import ExcelWriter
from ConnectorBinary import BinaryReader, BinaryWriter
from releaseNotes import getNotes, getBanner
from customLog import init_log

__author__ = "Serge LASSABE"
__copyright__ = "Copyright (C) 2023, Serge LASSABE"
__license__ = "agpl-3.0"
__version__ = "5.0.1"

'''
    Manage informations about conversion process :
    - check_if_changed : return the new 'model checksum' if changed from previous conversion process
    - write_last_conversion : serialize current conversion informations
    - read_last_conversion : deserialize previous conversion informations
    'model checksum' is a basic digest from LeanIX content
'''


def write_last_conversion(filename, checksum, when, version):
    # Write a digest to check when a model is modified
    with open(filename, 'w') as output:
        json.dump({'checksum': checksum, 'date': when,
                  'version': version}, output)


def read_last_conversion(filename):
    data = {}
    try:
        with open(filename, 'r') as input:
            data = json.load(input)
    except FileNotFoundError:
        logger.error(f"{filename} not found")
    return data


def check_if_changed(model, checksum_filename, ws, when, changelog_filename):
    checksum_new = model.get_checksum()
    last_convert = read_last_conversion(checksum_filename)
    checksum_previous = last_convert.get('checksum')
    version_previous = last_convert.get('version')
    date_previous = last_convert.get('date')

    if (checksum_new == checksum_previous) and (__version__ == version_previous):
        logger.info(
            f"Model is not modified (checksum is {checksum_new}) - Converter is not modified (version is {__version__})")
        return {}
    else:
        if __version__ != version_previous:  # Create changelog
            with open(changelog_filename, 'w', encoding='utf-8') as output:
                output.write(getBanner() + getNotes())
                output.write(
                    f"Info de génération : \nDate : {when} - Version : {__version__}\n")
        logger.info(
            f"Change detected since {date_previous} :\n- previous checksum : {checksum_previous} - new checksum : {checksum_new}\n- previous version : {version_previous} - new version : {__version__}")
        return checksum_new


'''
    Publish message
'''


def inform(channel, title, message):
    ''' Send status on ntfy.sh '''
    url = 'https://ntfy.sh/' + channel
    resp = requests.post('https://ntfy.sh/' + channel,
                         data=message.encode(encoding='utf-8'),
                         headers={"Title": title})
    if resp.status_code != requests.codes.ok:
        logger.error(f'an error occured with url : {url}')
        resp.raise_for_status()
    errors = resp.json().get('errors')
    if errors:
        logger.error(errors)
    return resp


def launch_it(ws, leanix_url, leanix_token, sftp_srv, sftp_usr, sftp_pwd, ntfy_channel):
    """ Launch extract

    Args:
        ws (str): the LeanIx work space to extract
        test_mode (bool): for debugging purpose
    """
    when = datetime.datetime.now().strftime('%Y-%m-%d-%Hh%M')       # Timestamp
    _FULL = False
    _OUTPUT_DIR = Path('./output/')
    _EXPORT_FILE_LIGHT = f"leanix2archi-{ws}-light.xml"
    _EXPORT_EXCEL = f"Leanix2excel-{ws}.xlsx"
    _EXPORT_FILE_FULL = f"leanix2archi-{ws}-full.xml"
    _WARNING_FILE = f'warnings-{ws}.xlsx'
    # Where to retrieve and store the conversion context
    _CHECKSUM_FILENAME = f'last-conversion-{ws}.json'

    logger.info(f'{when} :  Exporting workspace {ws} ')
    inform(ntfy_channel, 'Export', 'Started')

    if False:
        # Parse binary file (result of a previous conversion) : used in debugging mode
        binary_reader_full = BinaryReader(f'Leanix2Binary-{ws}-full.binary')
        model_full = binary_reader_full.get_model()

        binary_reader_light = BinaryReader(f'Leanix2Binary-{ws}-light.binary')
        model_full = binary_reader_light.get_model()
    else:
        # Connect to LeanIX 
        graphQL_reader = GraphQLReader(leanix_url, ws, leanix_token, Model())
        # Populate the model with an extract restricted to Application and Interface
        graphQL_reader.populate(False)
        model_light = graphQL_reader.get_model()

        if _FULL :
            graphQL_reader = GraphQLReader(leanix_url, ws, leanix_token, Model())
            # Populate the model with a full extract
            graphQL_reader.populate(True)
            model_full = graphQL_reader.get_model()

        logger.info(model_light.get_statistics())

    checksum_new = check_if_changed(
        model_light, _CHECKSUM_FILENAME, ws, when, _OUTPUT_DIR / 'changelog.txt')

    if (checksum_new):    # Something changed in LeanIx or launched in test mode
        # (2) Create writers
        archi_writer_light = XmlArchiWriter(model_light)
        binary_writer_light = BinaryWriter(model_light)
        excel_writer_light = ExcelWriter(model_light)
        if _FULL :
            binary_writer_full = BinaryWriter(model_full)
            archi_writer_full = XmlArchiWriter(model_full)

        # (3) Dump Model in various format
        # Export in Binary format
        binary_writer_light.dump(f"Leanix2Binary-{ws}-light.binary")
        if _FULL :
            binary_writer_full.dump(f"Leanix2Binary-{ws}-full.binary")

        # Export in Archi format
        archi_writer_light.dump(_OUTPUT_DIR / _EXPORT_FILE_LIGHT, getNotes(ws, when))
        if _FULL :
            archi_writer_full.dump(_OUTPUT_DIR / _EXPORT_FILE_FULL, getNotes(ws, when))
        # Export in Excel format
        excel_writer_light.dump(_OUTPUT_DIR / _EXPORT_EXCEL)

        model_light.dump_warning(_OUTPUT_DIR / _WARNING_FILE)
        write_last_conversion(
            Path('./log/') / _CHECKSUM_FILENAME, checksum_new, when, __version__)

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(sftp_srv, username=sftp_usr, password=sftp_pwd, cnopts=cnopts) as sftp:
            sftp.put(_OUTPUT_DIR / _EXPORT_FILE_LIGHT)
            sftp.put(_OUTPUT_DIR / _EXPORT_EXCEL)
            sftp.put(_OUTPUT_DIR / _WARNING_FILE)

        inform(ntfy_channel, 'Export', 'Processed')


if __name__ == '__main__':
    logger = init_log('converter', 'converter.log', debug=False)
    try:
        launch_it(os.environ['LEANIX_WS'],
                  os.environ['LEANIX_URL'],
                  os.environ['LEANIX_TOKEN'],
                  os.environ['SFTP_SRV'],
                  os.environ['SFTP_USR'],
                  os.environ['SFTP_PWD'],
                  os.environ['NTFY_CHANNEL'])
    except:
        logger.exception('')
        sys.exit(1)
