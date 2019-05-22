import os
import tempfile
import json
from argparse import ArgumentParser
import jsonschema
import shutil

from red_connector_http.commons.schemas import ARCHIVE_SCHEMA
from red_connector_http.commons.helpers import fetch_file
from red_connector_http.commons.helpers import http_method_func, auth_method_obj, graceful_error


RECEIVE_DIR_DESCRIPTION = 'Receive input dir from HTTP(S) server.'
RECEIVE_DIR_VALIDATE_DESCRIPTION = 'Validate access data for receive-dir.'


def _receive_dir(access, local_dir_path, listing):
    with open(access) as f:
        access = json.load(f)

    http_method = http_method_func(access, 'GET')
    auth_method = auth_method_obj(access)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    tmp_dir_path = tempfile.mkdtemp()
    tmp_file_path = os.path.join(tmp_dir_path, 'archive')

    fetch_file(tmp_file_path, access['url'], http_method, auth_method, verify)

    shutil.unpack_archive(tmp_file_path, local_dir_path, access['archiveFormat'])
    shutil.rmtree(tmp_dir_path)


def _receive_dir_validate(access, listing):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, ARCHIVE_SCHEMA)


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
