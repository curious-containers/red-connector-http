from collections import OrderedDict

from red_connector_http.commons.cli_modes import cli_modes
from red_connector_http.version import VERSION

from red_connector_http.http_archive.receive_dir import receive_dir, receive_dir_validate
from red_connector_http.http_archive.receive_dir import RECEIVE_DIR_DESCRIPTION, RECEIVE_DIR_VALIDATE_DESCRIPTION


CLI_VERSION = '0.1'
SCRIPT_NAME = 'red-connector-http-archive'
DESCRIPTION = 'RED Connector HTTP Archive'
TITLE = 'modes'

MODES = OrderedDict([
    ('cli-version', {'main': lambda: print(CLI_VERSION), 'description': 'RED connector CLI version.'}),
    ('receive-dir', {'main': receive_dir, 'description': RECEIVE_DIR_DESCRIPTION}),
    ('receive-dir-validate', {'main': receive_dir_validate, 'description': RECEIVE_DIR_VALIDATE_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
