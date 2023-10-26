"""
This file contains an utility to generate a secret sequence used
by the TOTP module.
"""

from argparse import ArgumentParser
from totp import secret_generator

def get_arguments():
    """
    Configures Argparse.

    Returns:

        command-line arguments
    """
    parser = ArgumentParser(description="TOTP secret generator utility")
    parser.add_argument(
        '-s',
        '--secret_path',
        help='Output path to the secret file',
        required=True
    )
    return parser.parse_args()

def main():
    """
    Retrieve the arguments, generate TOTP, write it to a file.
    """
    args = get_arguments()
    with open(args.secret_path, 'w', encoding='ascii') as secret_file:
        secret_file.write(secret_generator().decode('ascii'))

if __name__ == '__main__':
    main()
