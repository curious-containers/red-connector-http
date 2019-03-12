import os
import json
import subprocess
from argparse import ArgumentParser

from red_connector_http.commons.helpers import validate, find_executables
from red_connector_http.commons.schemas import MOUNT_DIR_SCHEMA


MOUNT_DIR_DESCRIPTION = 'Mount dir from SSH server.'
MOUNT_DIR_VALIDATE_DESCRIPTION = 'Validate access data for mount-dir.'

UMOUNT_DIR_DESCRIPTION = 'Unmout directory previously mounted via mount-dir.'


def _mount_dir(access, local_dir_path):
    with open(access) as f:
        access = json.load(f)

    url = access['url']
    path = local_dir_path

    httpdirfs_executable, _ = find_executables()

    command = [httpdirfs_executable]

    # add authentication
    auth = access.get('auth')
    if auth:
        command.extend([
            '--username',
            '\'{}\''.format(auth['username']),
            '--password',
            '\'{}\''.format(auth['password']),
        ])

    command.extend([
        url,
        path
    ])

    command = ' '.join(command)

    os.mkdir(path)

    process_result = subprocess.run(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        shell=True
    )

    if process_result.returncode != 0:
        if os.path.isdir(path):
            os.rmdir(path)
        if auth:
            raise Exception('Could not mount from "{}" for user "{}" using "{}":\n{}'
                            .format(url, auth['username'], httpdirfs_executable, process_result.stderr.decode('utf-8')))
        else:
            raise Exception('Could not mount from "{}" using "{}" without authentication:\n{}'
                            .format(url, httpdirfs_executable, process_result.stderr.decode('utf-8')))


def _mount_dir_validate(access):
    with open(access) as f:
        access = json.load(f)

    validate(access, MOUNT_DIR_SCHEMA)
    _ = find_executables()


def _umount_dir(local_dir_path):
    _, fusermount_executable = find_executables()

    process_result = subprocess.run([fusermount_executable, '-u', local_dir_path], stderr=subprocess.PIPE)
    if process_result.returncode != 0:
        raise Exception(
            'Could not unmount local_dir_path={local_dir_path} via {fusermount_executable}:\n{error}'.format(
                local_dir_path=local_dir_path,
                fusermount_executable=fusermount_executable,
                error=process_result.stderr
            )
        )


def mount_dir():
    parser = ArgumentParser(description=MOUNT_DIR_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local dir path.'
    )
    args = parser.parse_args()
    _mount_dir(**args.__dict__)


def mount_dir_validate():
    parser = ArgumentParser(description=MOUNT_DIR_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _mount_dir_validate(**args.__dict__)


def umount_dir():
    parser = ArgumentParser(description=UMOUNT_DIR_DESCRIPTION)
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local output dir path.'
    )
    args = parser.parse_args()
    _umount_dir(**args.__dict__)
