import yaml
from hashlib import sha256
from logging import info

class Address_book:

    def __init__(self, addr_file_path):
        self.addr_file_path = addr_file_path

    def init_emails(self):
        index_exists = self.addr_file_path.is_file()
        index_filled = self.addr_file_path.stat().st_size == 0
        if not index_exists or not index_filled:
            with open(self.addr_file_path, 'w') as index_file:
                index_file.write('[]')

    async def read_emails(self):
        emails = None
        try:
            with open(self.addr_file_path, 'r') as addr_file:
                emails = yaml.safe_load(addr_file)
        except FileNotFoundError as e:
            info('fnf')
            pass
        emails = emails or []
        info(f'Loaded {len(emails)} email addresses')
        return emails

    async def add_email(self, email: str):
        unique = True
        email = email.strip().lower()
        hash = sha256(email.encode('ascii')).hexdigest()
        record = {'email': email, 'hash': hash}
        emails = await self.read_emails()
        if list(filter(lambda record: record['email'] == email, emails)):
            unique = False
        emails = [addr for addr in emails if addr['email'].strip() != email]
        emails.append(record)
        with open(self.addr_file_path, 'w') as x_file:
            yaml.safe_dump(emails, x_file)
        return unique

    async def pop_key(self, key: str, key_type: str):
        result = None
        emails = await self.read_emails()
        removed = list(filter(lambda record: record[key_type] == key, emails))
        if removed:
            result = removed[0]
        emails = list(filter(lambda record: record[key_type] != key, emails))
        with open(self.addr_file_path, 'w') as addr_file:
            yaml.safe_dump(emails, addr_file)        
        return result
