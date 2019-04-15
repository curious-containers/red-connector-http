import json
from argparse import ArgumentParser

from jsonschema import validate

from red_connector_http.commons.schemas import SCHEMA
from red_connector_http.commons.helpers import http_method_func, auth_method_obj


RECEIVE_FILE_DESCRIPTION = 'Receive JSON input from HTTP(S) server.'
RECEIVE_FILE_VALIDATE_DESCRIPTION = 'Validate access data for receive-file.'

SEND_FILE_DESCRIPTION = 'Send JSON output to HTTP(S) server.'
SEND_FILE_VALIDATE_DESCRIPTION = 'Validate access data for send-file.'


def _receive_file(access, local_file_path):
    http_method = http_method_func(access, 'GET')
    auth_method = auth_method_obj(access)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    r = http_method(
        access['url'],
        auth=auth_method,
        verify=verify
    )
    r.raise_for_status()
    data = r.json()

    with open(local_file_path, 'wb') as f:
        json.dump(data, f)


def _receive_file_validate(access):
    validate(access, SCHEMA)


def _send_file(access, local_file_path):
    http_method = http_method_func(access, 'POST')
    auth_method = auth_method_obj(access)

    with open(local_file_path) as f:
        data = json.load(f)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    r = http_method(
        access['url'],
        json=data,
        auth=auth_method,
        verify=verify,
        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
    )
    r.raise_for_status()


def _send_file_validate(access):
    validate(access, SCHEMA)


def receive_file():
    parser = ArgumentParser(description=RECEIVE_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local input file path.'
    )
    args = parser.parse_args()
    _receive_file(**args.__dict__)


def receive_file_validate():
    parser = ArgumentParser(description=RECEIVE_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_file_validate(**args.__dict__)


def send_file():
    parser = ArgumentParser(description=SEND_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local output file path.'
    )
    args = parser.parse_args()
    _send_file(**args.__dict__)


def send_file_validate():
    parser = ArgumentParser(description=SEND_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_file_validate(**args.__dict__)