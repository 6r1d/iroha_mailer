"""
Address book utilities.
"""

from os import urandom
from hashlib import sha1
from logging import info, error
from yaml import safe_dump, safe_load

class AddressBook:
    """
    Address book manipulation class.
    The address book is a list of emails and their hashes.
    """

    def __init__(self, addr_file_path):
        self.addr_file_path = addr_file_path

    def init_emails(self):
        """
        Create an address book file.
        """
        index_exists = self.addr_file_path.is_file()
        index_filled = self.addr_file_path.stat().st_size == 0
        if not index_exists or not index_filled:
            with open(self.addr_file_path, 'w', encoding='utf-8') as index_file:
                index_file.write('---')

    async def read_emails(self):
        """
        Returns:
            (dict) hashes as keys, emails as values
        """
        emails = []
        try:
            with open(self.addr_file_path, 'r', encoding='utf-8') as addr_file:
                emails = safe_load(addr_file)
        except FileNotFoundError:
            error(f'File not found: {self.addr_file_path}')
        info(f'Loaded {len(emails)} email addresses')
        return emails

    async def add_email(self, email: str):
        """
        Adds an email.
        Returns True if it isn't present in the file.
        """
        unique = True
        email = email.strip().lower()
        mail_hash = sha1(email.encode('ascii') + urandom(8)).hexdigest()
        emails = await self.read_emails()
        if not isinstance(emails, dict):
            emails = {}
        for _, tmp_email in emails.items():
            if tmp_email == email:
                unique = False
        emails[mail_hash] = email
        with open(self.addr_file_path, 'w', encoding='utf-8') as x_file:
            safe_dump(emails, x_file)
        return unique

    async def pop_hash(self, mail_hash: str):
        """
        Removes the email by its hash. Used for unsubscription.

        Returns:
            the unsubscribed user's email
        """
        emails = await self.read_emails()
        result = emails.pop(mail_hash, None)
        with open(self.addr_file_path, 'w', encoding='utf-8') as addr_file:
            safe_dump(emails, addr_file)
        return result
