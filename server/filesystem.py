"""
Common filesystem functions.
"""

from pathlib import Path
from os import path as os_path

def get_code_dir():
    """
    Returns:
        (Path): a path to the parent directory, relative to the current file
    """

    return Path(os_path.dirname(os_path.realpath(__file__)))
