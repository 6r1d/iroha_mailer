"""
Hash generation functions.
"""

from string import ascii_letters, digits
from random import choice

def generic_id_generator(size, chars) -> str:
    """
    Generate a random hash.
    """
    return ''.join(choice(chars) for _ in range(size))

def file_id_generator(size=6, chars=ascii_letters+digits) -> str:
    """
    Generate a random hash for the temp files.
    """
    return generic_id_generator(size, chars)
