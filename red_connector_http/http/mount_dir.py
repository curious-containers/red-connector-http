import os
import json
import subprocess
from argparse import ArgumentParser

import jsonschema

from red_connector_http.commons.helpers import find_mount_executables, graceful_error, find_httpdirfs_executable, \
    find_umount_executable
from red_connector_http.commons.schemas import MOUNT_DIR_SCHEMA


MOUNT_DIR_DESCRIPTION = 'Mount dir from SSH server.'
MOUNT_DIR_VALIDATE_DESCRIPTION = 'Validate access data for mount-dir.'

UMOUNT_DIR_DESCRIPTION = 'Unmout directory previously mounted via mount-dir.'


def _mount_dir(access, local_dir_path):
    with open(access) as f:
        access = json.load(f)

    url = access['url']

    use_pwd, path = os.path.split(os.path.normpath(local_dir_path))

    if len(path) > 64:
        raise Exception('httpdirfs does not support paths, which contain more than 64 characters. The given path "{}"'
                        'contains {} characters.'.format(path, len(path)))

    httpdirfs_executable = find_httpdirfs_executable()

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

    use_cache = access.get('cache')
    if use_cache:
        command.append('--cache')

    command.extend([
        url,
        path
    ])

    command = ' '.join(command)

    os.mkdir(local_dir_path)

    process_result = subprocess.run(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        shell=True,
        cwd=use_pwd
    )

    # check if execution was successful and target directory contains something, because httpdirfs does have
    # return code 0 under certain circumstances even if it fails to mount
    if (process_result.returncode != 0) or (len(os.listdir(local_dir_path)) == 0):
        if os.path.isdir(local_dir_path):
            os.rmdir(local_dir_path)
        if auth:
            raise Exception('Could not mount from "{}" for user "{}" using "{}":\n{}'
                            .format(url, auth['username'], httpdirfs_executable, process_result.stderr.decode('utf-8')))
        else:
            raise Exception('Could not mount from "{}" using "{}" without authentication:\n{}'
                            .format(url, httpdirfs_executable, process_result.stderr.decode('utf-8')))


def _mount_dir_validate(access):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, MOUNT_DIR_SCHEMA)
    _ = find_mount_executables()


def _umount_dir(local_dir_path):
    fusermount_executable = find_umount_executable()

    process_result = subprocess.run([fusermount_executable, '-u', local_dir_path], stderr=subprocess.PIPE)
    if process_result.returncode != 0:
        raise Exception(
            'Could not unmount local_dir_path={local_dir_path} via {fusermount_executable}:\n{error}'.format(
                local_dir_path=local_dir_path,
                fusermount_executable=fusermount_executable,
                error=process_result.stderr
            )
        )


@graceful_error
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


@graceful_error
def mount_dir_validate():
    parser = ArgumentParser(description=MOUNT_DIR_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _mount_dir_validate(**args.__dict__)


@graceful_error
def umount_dir():
    parser = ArgumentParser(description=UMOUNT_DIR_DESCRIPTION)
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local output dir path.'
    )
    args = parser.parse_args()
    _umount_dir(**args.__dict__)
