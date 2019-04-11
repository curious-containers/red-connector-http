import os
import json
from argparse import ArgumentParser
from copy import deepcopy

import jsonschema

from red_connector_http.commons.schemas import SCHEMA
from red_connector_http.commons.helpers import ListingError, build_path, fetch_directory
from red_connector_http.commons.helpers import http_method_func, auth_method_obj, graceful_error


RECEIVE_DIR_DESCRIPTION = 'Receive input dir from HTTP(S) server.'
RECEIVE_DIR_VALIDATE_DESCRIPTION = 'Validate access data for receive-dir.'


def _receive_dir(access, local_dir_path, listing):
    with open(access) as f:
        access = json.load(f)

    if listing is None:
        raise ListingError('red-connector-http receive-dir requires listing.')

    with open(listing) as f:
        listing = json.load(f)

    listing = deepcopy(listing)

    build_path(access['url'], listing, 'complete_url')
    build_path(local_dir_path, listing, 'complete_path')

    http_method = http_method_func(access, 'GET')
    auth_method = auth_method_obj(access)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    if not os.path.exists(local_dir_path):
        os.mkdir(local_dir_path)

    fetch_directory(listing, http_method, auth_method, verify)


def _receive_dir_validate(access, listing):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, SCHEMA)
    if listing is None:
        raise ListingError('red-connector-http receive-dir-validate requires listing.')

    with open(listing) as f:
        # TODO validate listing
        json.load(f)


@graceful_error
def receive_dir():
    parser = ArgumentParser(description=RECEIVE_DIR_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local input dir path.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_dir(**args.__dict__)


@graceful_error
def receive_dir_validate():
    parser = ArgumentParser(description=RECEIVE_DIR_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_dir_validate(**args.__dict__)
