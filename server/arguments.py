"""
This module provides a function with Argparse configuration
for the server.
"""

from argparse import ArgumentParser

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
    return parser.parse_args()
