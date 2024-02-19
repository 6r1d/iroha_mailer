"""
This module is used to send mail synchronously
through the GMail API.
"""

import base64
from os.path import exists
from email.mime.multipart import MIMEMultipart
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from errors import SendingError, GmailAPICredentialsError, GmailAPITokenRefreshError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def prepare_credentials(token_path: str) -> Credentials | None:
    """
    Returns:
        Credentials: the GMail credentials instance.
    """
    credentials = None
    # The file token.json stores the user's access and refresh tokens,
    # and is created automatically when the authorization flow
    # completes for the first time.
    if exists(token_path):
        try:
            credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        except ValueError:
            # If the token is expired, it will be updated later
            pass
    # If there are no (valid) credentials available, refresh them.
    if not credentials or not credentials.valid:
        try:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Save the credentials for the next run
                with open(token_path, 'w', encoding='utf-8') as token:
                    token.write(credentials.to_json())
            else:
                err_text = (
                    'Unable to refresh the credentials: '
                    'invalid or expired file.\n'
                    'user\'s browser interaction required;'
                    'refresh according to the documentation.'
                )
                raise GmailAPICredentialsError(err_text)
        except RefreshError as ref_err:
            raise GmailAPITokenRefreshError(
                f'Unable to refresh credentials token: {str(ref_err)}'
            ) from ref_err
    return credentials

def build_gmail_service(credentials: Credentials):
    """
    Returns:
        an authenticated Gmail API service or None.
    """
    result = None
    try:
        result = build('gmail', 'v1', credentials=credentials)
    except HttpError:
        pass
    return result

def send_gmail(
    message: MIMEMultipart,
    service: Resource
):
    """
    Send an email via the Gmail API.

    Args:
        msg (MIMEMultipart): email message
        service (Resource): GMail API service
    """
    # The body needs to be encoded in base64url format.
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    # Send the message
    try:
        message = (service.users().messages().send(userId='me', body=body).execute())
        print(f'Message Id: {message.get("id")}')
    except HttpError as err:
        raise SendingError(err.reason, 'GMail') from err
