#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Token management : keep credentials secret
'''

import requests
from customLog import get_default_logger

__author__ = "Serge LASSABE"
__copyright__ = "Copyright (C) 2023, Serge LASSABE"
__license__ = "agpl-3.0"
__version__ = "5.0.1"


def create_credential(base, token):
    logger = get_default_logger()
    auth_url = f'https://{base}/services/mtm/v1/oauth2/token'

    resp = requests.post(auth_url,
                         auth=('apitoken', token),
                         data={'grant_type': 'client_credentials'})
    if resp.status_code != requests.codes.ok:
        logger.error(f'!! create_credential : error for url = {auth_url}')
        resp.raise_for_status()

    access_token = resp.json()['access_token']
    return access_token
