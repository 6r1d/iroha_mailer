"""
This module provides functions to manage the rotation
of the unsent letters.
"""

import asyncio
from json import dump, JSONDecodeError
from pathlib import Path
from logging import exception
from datetime import datetime, timedelta

from mime_email import configure_multipart
from smtp_sender import smtp_send
from gmail_api_sender import prepare_credentials, build_gmail_service, send_gmail
from hash import file_id_generator
from errors import GmailAPICredentialsError, GmailAPITokenRefreshError, SendingError

from serialization import load_json_file

GMAIL_CREDENTIALS_REFRESH_MINUTES = 30
SENDING_DELAY_MINUTES = 30

def queue_email_rotation(rotation_path: Path, email_data: dict):
    """
    Saves an email JSON data to be rotated.

    Arguments:
        rotation_path (Path): a path to the rotation directory
        email_data (dict): the data for a single email to be sent
                           like its text, the recepient's address, etc. 
    """
    rotated_file_path = rotation_path / f'{file_id_generator()}.json'
    with open(rotated_file_path, 'w', encoding='utf-8') as rotated_file:
        dump(email_data, rotated_file)

def find_single_file(directory_path, extension):
    """
    Find a single file in the specified directory.

    Args:
        directory_path (str or Path): The path to the directory to search for a JSON file.
        extension (str): File extension, e.g., 'json'

    Returns:
        Path or None: Returns the path to the found file or None if not found.
    """
    directory = Path(directory_path)
    if directory.is_dir():
        for file_path in directory.glob(f'*.{extension}'):
            return file_path
    return None

class Rotator:
    """
    Controls an internal rotation mechanism.
    """

    def __init__(self, rotation_path: Path, config):
        """
        Arguments:
            rotation_path (pathlib.Path): Path to check.
        """
        self.rotation_path = rotation_path
        self.config = config
        # A dictionary of datetimes to check time intervals
        self.timers = {}
        # Should a delay be applied to sending?
        # (Depends on the last success)
        self.sending_delay = False
        self.setup_timer('send_mail')
        # GMail credentials and timing
        self.gmail_credentials = None
        self.setup_timer('gmail_credentials_refresh')
        if self.config.get_mailing_mode() == 'GMail':
            self.refresh_gmail_credentials()

    def setup_timer(self, name):
        """
        Used to track the start or reset time of an event,
        identified by a unique name.
        If a timer with the same name already exists, it will be
        overwritten with the current time.

        Arguments:
            name (str): The name of the timer to set or reset.
        """
        self.timers[name] = datetime.now()

    def check_timer_delta(self, name, minutes, autoreset=False):
        """
        Checks if the specified number of minutes have passed since the timer,
        identified by `name`, was set.
        Optionally, resets the timer if the time elapsed meets or exceeds
        the specified duration.

        Arguments:
            name (str): The name of the timer to check.
            minutes (int): The number of minutes to check against the timer's elapsed time.
            autoreset (bool, optional): Whether to reset the timer if the time condition is met.

        Returns:
            bool: True if the specified number of minutes have passed since the timer was set,
                  False otherwise.
        """
        now = datetime.now()
        # Check how much time passed
        time_diff = self.timers[name] - now
        # Check if the difference is greater than
        # or equal to the specified minutes
        result = time_diff >= timedelta(minutes=minutes)
        # Reset the timer if needed
        if result and autoreset:
            self.setup_timer(name)
        return result

    def refresh_gmail_credentials(self):
        """
        Updates the GMail credentials.

        When a credentials issue is encountered, it's optimal to fail,
        but since the Docker run is the target, looping between failures
        and pinging Google is counterproductive.
        Relying on credential refresh mechanism to ping Google slowly
        is less counterproductive.
        """
        try:
            gmail_opts = self.config.get_gmail_api()
            self.gmail_credentials = prepare_credentials(gmail_opts.get('token_path'))
        except GmailAPICredentialsError as cred_error:
            exception(cred_error)
        except GmailAPITokenRefreshError as token_error:
            exception(token_error)
        self.gmail_service = build_gmail_service(self.gmail_credentials)
        print(self.gmail_service)

    async def send_email(self, data: dict):
        """
        Sends an individual email using SMTP or GMail API
        depending on a configured mailing mode
        """
        mail_msg = await configure_multipart(
            text=data.get('text'),
            list_unsubscribe=data.get('unsubscribe_url'),
            subject=data.get('subject'),
            sender=data.get('sender'),
            to=data.get('recipient')
        )
        if self.config.get_mailing_mode() == 'SMTP':
            await smtp_send(
                mail_msg, **self.config.get_smtp()
            )
        else:
            if self.gmail_service:
                send_gmail(mail_msg, self.gmail_service)
            else:
                raise SendingError('Unable to retrieve a GMail service', 'GMail')

    async def send_single_email(self):
        """
        Loads a rotation file and sends a single email.

        Uses an internal delay mechanism to balance the delays given unsuccessful
        attempts.
        Updates the rotation delays if there's an issue.
        Removes the sending delays if there's no issue with sending the last email.
        """
        sent = None
        rotated_file = find_single_file(self.rotation_path, 'json')
        if rotated_file:
            # Try to load a single email, handle the possible exceptions
            email_data = None
            try:
                email_data = load_json_file(rotated_file)
            except FileNotFoundError:
                exc_text = (
                    f'Rotated file not found: "{rotated_file}".\n'
                    'Check if other mailer instance is running.'
                )
                exception(exc_text)
            except JSONDecodeError:
                exc_text = (
                    f'Invalid JSON found in "{rotated_file}".\n'
                    'Please update the mailer code and delete the file.'
                )
            try:
                if email_data:
                    await self.send_email(email_data)
                    sent = True
                    self.sending_delay = False
            except SendingError as send_err:
                exception(send_err)
                sent = False
                self.sending_delay = True
                self.setup_timer('send_mail')
        if sent:
            # Remove a rotated file as it isn't needed
            rotated_file.unlink()

    def check_sending_allowed(self):
        """
        Check that there's no timer blocking the sending.
        """
        result = False
        if self.sending_delay is False:
            result = True
        if self.check_timer_delta(
            'send_mail',
            SENDING_DELAY_MINUTES,
            True
        ):
            result = True
        return result

    async def rotate(self, ms, sleep_interval=1):
        """
        Checks the path to unsent messages
        and sends them later to ensure they are sent.

        Args:
            ms (MailServer): a server instance
            rotation_path (pathlib.Path): Path to check.
            sleep_interval (int): Check delay in seconds.
        """
        while ms.running:
            if self.check_sending_allowed():
                await self.send_single_email()
            if self.check_timer_delta(
                'gmail_credentials_refresh',
                GMAIL_CREDENTIALS_REFRESH_MINUTES,
                autoreset=True
            ):
                self.refresh_gmail_credentials()
            await asyncio.sleep(sleep_interval)
