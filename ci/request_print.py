"""
Print version request utility to be integrated in CI.
"""

from asyncio import run
from argparse import ArgumentParser, Action
from totp import gen_otp_from_secret_file
from common_req import perform_print_request

class FixRouteAction(Action):
    """
    Fixes the route, adding the "/generate_print" part.
    """

    def __call__(self, parser, args, value, option_string=None):
        value = value.removesuffix('/generate_print').removesuffix('/generate_print/')
        setattr(args, self.dest, f'{value}/generate_print')

def get_arguments():
    """
    Retrieves the Argparse arguments.
    """

    parser = ArgumentParser(description="Print version requester utility")
    parser.add_argument(
        '-s',
        '--secret_path',
        help='Path to the secret file for the TOTP generator',
        required=True
    )
    parser.add_argument(
        '-a',
        '--address',
        help="HTTP address",
        required=True,
        action=FixRouteAction
    )
    parser.add_argument(
        '-d',
        "--data_path",
        help="Path to the data file",
        required=True
    )
    parser.add_argument(
        '-o',
        "--output_path",
        help="Path to the output HTML file",
        required=True
    )
    return parser.parse_args()

async def main():
    """
    Load arguments, prepare a one-time pass, perform a request for CI.
    """

    args = get_arguments()
    totp = gen_otp_from_secret_file(args.secret_path)
    html_render_str = await perform_print_request(
        args.address, args.data_path, totp
    )
    with open(args.output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(html_render_str)

if __name__ == '__main__':
    run(main())
