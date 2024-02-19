"""
This module is used to send mail synchronously
through the GMail API.
"""

import base64
from argparse import ArgumentParser, Namespace, ArgumentTypeError
from os.path import exists
from pathlib import Path
from shutil import copy
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def prepare_credentials(credentials_path: str, token_path: str) -> Credentials | None:
    credentials = None
    # The file token.json stores the user's access and refresh tokens,
    # and is created automatically when the authorization flow
    # completes for the first time.
    if exists(token_path):
        credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w', encoding='utf-8') as token:
            token.write(credentials.to_json())
    return credentials

def validate_file_path(path_str):
    """
    Validate the file path argument to ensure it exists and is a file.
    Returns a pathlib.Path object if valid, raises an error otherwise.
    """
    path = Path(path_str)
    if not path.is_file():
        raise ArgumentTypeError(f'The path {path_str} is not a valid file.')
    return path

def safe_remove_file(fp: Path) -> None:
    """Safely removes a file at the given pathlib.Path.

    This function attempts to remove a file specified by the `path` argument.
    If the path does not exist, refers to a directory,
    or if the removal fails for any other reason, it will catch
    the exception instead of raising it.

    Args:
        path: A pathlib.Path object representing the file to be removed.

    Returns:
        None
    """
    try:
        if fp.is_file():
            fp.unlink()
    except FileNotFoundError as e:
        pass

def get_arguments() -> Namespace:
    parser = ArgumentParser(description='GMail token updater.')
    parser.add_argument(
        '--credential_file',
        '-c',
        type=validate_file_path,
        help='File path to a credential file.',
        required=True
    )
    args = parser.parse_args()
    return args

def main():
    args = get_arguments()
    # Find a working directory
    parent_directory = Path(__file__).parent
    # Find the credential files that are already registered
    target_cred_file = parent_directory.parent / 'config/gmail_credentials.json'
    target_token_file = parent_directory.parent / 'config/gmail_token.json'
    # Clean up the credential files
    safe_remove_file(target_cred_file)
    safe_remove_file(target_token_file)
    # Copy the credential file
    open(target_cred_file, 'a').close()
    copy(args.credential_file, target_cred_file)
    # Perform the API request to write a token
    prepare_credentials(target_cred_file, target_token_file)

if __name__ == "__main__":
    main()
