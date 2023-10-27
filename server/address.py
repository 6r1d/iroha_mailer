"""
Address book utilities.
"""

from hashlib import sha256
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
                index_file.write('[]')

    async def read_emails(self):
        """
        Returns a list of emails with their hashes.
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
        """
        unique = True
        email = email.strip().lower()
        mail_hash = sha256(email.encode('ascii')).hexdigest()
        record = {'email': email, 'hash': mail_hash}
        emails = await self.read_emails()
        if list(filter(lambda record: record['email'] == email, emails)):
            unique = False
        emails = [addr for addr in emails if addr['email'].strip() != email]
        emails.append(record)
        with open(self.addr_file_path, 'w', encoding='utf-8') as x_file:
            safe_dump(emails, x_file)
        return unique

    async def pop_key(self, key: str, key_type: str):
        """
        Removes and returns a key.
        Used for unsubscription.
        """
        result = None
        emails = await self.read_emails()
        removed = list(filter(lambda record: record[key_type] == key, emails))
        if removed:
            result = removed[0]
        emails = list(filter(lambda record: record[key_type] != key, emails))
        with open(self.addr_file_path, 'w', encoding='utf-8') as addr_file:
            safe_dump(emails, addr_file)
        return result
