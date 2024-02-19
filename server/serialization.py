"""
This module isolates the serialisation-related code.
"""

from typing import Any
from json import load, JSONDecodeError
from pathlib import Path

def load_json_file(file_path: Path) -> Any:
    """
    Loads and returns the contents of a JSON file.

    Given a pathlib.Path instance pointing to a JSON file, this function
    opens the file, loads its contents using the json module, and then
    returns the data. The function is capable of loading any JSON content,
    including objects, arrays, strings, numbers, booleans, or null.

    Parameters:
    - file_path (Path): A pathlib.Path instance pointing to the JSON file to be loaded.

    Returns:
    - Any: The content of the JSON file, which can be a dictionary, a list,
           or any basic JSON data type depending on the file's contents.

    Raises:
    - FileNotFoundError: If the file_path does not exist.
    - json.JSONDecodeError: If the file contains invalid JSON.
    - Exception: For any other issues that arise during file opening or reading.

    Example usage:
    >>> data = load_json_file(Path('/path/to/file.json'))
    >>> print(data)
    """
    try:
        with file_path.open('r', encoding='utf-8') as file:
            return load(file)
    except FileNotFoundError as fnf_error:
        raise FileNotFoundError(
            f"The file {file_path} was not found."
        ) from fnf_error
    except JSONDecodeError as decode_error:
        raise JSONDecodeError(
            f"Error decoding JSON content from {file_path}.",
            decode_error.doc,
            decode_error.pos
        ) from decode_error
