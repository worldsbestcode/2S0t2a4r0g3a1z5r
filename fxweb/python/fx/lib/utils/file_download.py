"""
@file      file_download.py
@author    Matthew Seaworth (mseaworth@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2017

@section DESCRIPTION
Utilities for file serialization
"""
import os
import tempfile
from datetime import datetime, timedelta

DOWNLOAD_TEMP_DIR = '/var/run/fx/tmp/webdownload'
DOWNLOAD_READ_SIZE = 4096


def is_safe_path(base, path, follow_symlinks=True):
    """Validate that a path is what we expect it to be
    Arguments:
        base: The directory we expect to prepend the resolved path
        path: The path to check for safety
        follow_symlinks: If we want to follow symlinks when traversing paths
    Returns: True if the path matches the expected path
    """
    if follow_symlinks:
        return os.path.realpath(path).startswith(base)

    return os.path.abspath(path).startswith(base)


def is_safe_dir(directory):
    """Validate that a directory is what we expect it to be
    Arguments:
        directory: The directory to check
    Return: True if the path is a directory without any path manipulation
    """
    return os.path.isdir(directory) and \
        is_safe_path(directory, directory, follow_symlinks=True)


def temp_filename(dir_path=DOWNLOAD_TEMP_DIR):
    """Make a temporary filename"""
    if is_safe_dir(dir_path):
        tempfile.tempdir = dir_path

    while True:
        with tempfile.NamedTemporaryFile() as temp:
            name = temp.name
            temp.close()
            yield name


def list_download_dir(dir_path=DOWNLOAD_TEMP_DIR):
    """Convenience function to list the download files
    Returns: file_list Containing the list of files
    """
    if not is_safe_dir(dir_path):
        return []

    file_list = []
    for report in os.listdir(dir_path):
        file_path = '/'.join([dir_path, report])
        if os.path.isfile(file_path):
            file_list.append(file_path)

    return file_list


def init_download_dir(dir_path=DOWNLOAD_TEMP_DIR):
    """Initialize the temporary download directory"""
    for file_path in list_download_dir(dir_path):
        os.remove(file_path)


def prune_download_dir(dir_path=DOWNLOAD_TEMP_DIR):
    """Remove old files from the download dir"""
    for file_path in list_download_dir(dir_path):
        modify_date = datetime.fromtimestamp(os.path.getmtime(file_path))
        if datetime.now() > modify_date + timedelta(hours=1):
            os.remove(file_path)
