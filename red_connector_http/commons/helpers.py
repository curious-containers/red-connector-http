import os
import jsonschema
from shutil import which

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


FUSERMOUNT_EXECUTABLES = ['fusermount3', 'fusermount']
HTTPDIRFS_EXECUTABLES = ['httpfirfs']


class ValidationError(Exception):
    pass


class ListingError(Exception):
    pass


def find_executables():
    httpdirfs_executable = None
    for executable in FUSERMOUNT_EXECUTABLES:
        if which(executable):
            httpdirfs_executable = executable
            break
    if not httpdirfs_executable:
        raise Exception('One of the following executables must be present in PATH: {}'.format(
            HTTPDIRFS_EXECUTABLES
        ))

    fusermount_executable = None
    for executable in FUSERMOUNT_EXECUTABLES:
        if which(executable):
            fusermount_executable = executable
            break
    if not fusermount_executable:
        raise Exception('One of the following executables must be present in PATH: {}'.format(
            FUSERMOUNT_EXECUTABLES
        ))

    return httpdirfs_executable, fusermount_executable


def http_method_func(access, default):
    http_method = access.get('method', default).lower()

    if http_method == 'get':
        return requests.get
    if http_method == 'put':
        return requests.put
    if http_method == 'post':
        return requests.post

    raise Exception('Invalid HTTP method: {}'.format(http_method))


def auth_method_obj(access):
    if not access.get('auth'):
        return None

    auth = access['auth']
    auth_method = auth.get('method', 'basic').lower()

    if auth_method == 'basic':
        return HTTPBasicAuth(
            auth['username'],
            auth['password']
        )
    if auth_method == 'digest':
        return HTTPDigestAuth(
            auth['username'],
            auth['password']
        )

    raise Exception('Invalid auth method: {}'.format(auth_method))


def fetch_file(file_path, url, http_method, auth_method, verify=True):
    """
    Fetches the given file. Assumes that the directory in which this file is stored is already present in the local
    filesystem.

    :param file_path: The path where the file content should be stored
    :param url: The url from where to fetch the file
    :param http_method: An function object, which returns a requests result,
    if called with (url, auth=auth_method, verify=verify, stream=True)
    :param auth_method: An auth_method, which can be used as parameter for requests.http_method
    :param verify: A boolean indicating if SSL Certification should be used.

    :raise requests.exceptions.HTTPError: If the HTTP requests could not be resolved correctly.
    """

    r = http_method(
        url,
        auth=auth_method,
        verify=verify,
        stream=True
    )
    r.raise_for_status()

    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)

    r.raise_for_status()


def fetch_directory(listing, http_method, auth_method, verify=True):
    """
    :param listing: A complete listing with complete urls for every containing file.
    :param http_method: An function object, which returns a requests result,
    if called with (url, auth=auth_method, verify=verify, stream=True)
    :param auth_method: An auth_method, which can be used as parameter for requests.http_method
    :param verify: A boolean indicating if SSL Certification should be used.

    :raise requests.exceptions.HTTPError: If a HTTP requests could not be resolved correctly.
    """

    for sub in listing:
        if sub['class'] == 'File':
            fetch_file(sub['complete_path'], sub['complete_url'], http_method, auth_method, verify)
        elif sub['class'] == 'Directory':
            os.mkdir(sub['complete_path'])
            if 'listing' in sub:
                fetch_directory(sub['listing'], http_method, auth_method, verify)


def build_path(base_path, listing, key):
    """
    Builds a list of string representing urls, which are build by the base_url and the subfiles and subdirectories
    inside the listing. The resulting urls are written to the listing with the key 'complete_url'

    :param base_path: A string containing the base path
    :param listing: A dictionary containing information about the directory structure of the given base_url
    :param key: The key under which the complete url is stored
    """

    for sub in listing:
        path = os.path.join(base_path, sub['basename'])
        sub[key] = path
        if sub['class'] == 'Directory':
            if 'listing' in sub:
                build_path(path, sub['listing'], key)


def validate(instance, schema):
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as e:
        if hasattr(e, 'context') and e.context is not None:
            raise ValidationError(str(e.context))
        else:
            raise ValidationError(str(e))
