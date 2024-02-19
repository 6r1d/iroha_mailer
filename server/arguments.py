"""
This module provides a function with Argparse configuration
for the server.
"""

from argparse import ArgumentParser
from os.path import isdir
from pathlib import Path

def dir_path(dpath: str) -> Path:
    """
    Ensure that the supplied input is a valid directory path.

    Args:
        dpath (str): input directory location

    Returns:
        Path: A Path object representing the validated directory path.

    Raises:
        NotADirectoryError: If the dpath does not exist or is not a directory.
    """
    if not isdir(dpath):
        raise NotADirectoryError(f'"{dpath}" is not a valid directory.')
    return Path(dpath)

def get_arguments():
    """
    Returns:

        (argparse.Namespace): a namespace with paths to configuration, email list, secret file.
                              Email list may be updated.
                              Configuration and the secret file are read-only.
    """
    parser = ArgumentParser(description="Soramitsu Iroha mailer")
    parser.add_argument('-c', "--config_path", help="Path to the configuration file", required=True)
    parser.add_argument('-e', "--emails_path", help="Path to the emails file", required=True)
    parser.add_argument('-s', "--secret_path", help="Path to the secret file", required=True)
    parser.add_argument('-r', "--rotation_path",
                        help="Path to the rotation directory",
                        type=dir_path,
                        required=True)
    return parser.parse_args()
