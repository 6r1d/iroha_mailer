"""
Mailer print version utility to be integrated in CI.
"""

from asyncio import run
from argparse import ArgumentParser, Action
from aiohttp import ClientSession
from aiohttp.formdata import FormData
from totp import gen_otp_from_secret_file

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

    async with ClientSession() as session:
        data = FormData()
        data.add_field('password', totp)
        with open(args.data_path, 'rb') as template_data:
            data.add_field('template_data', template_data.read())
        req = await session.post(args.address, data=data)
        if req.status == 200:
            print('The result was generated')
            with open(args.output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(
                    await req.text()
                )
        else:
            print(f'Unable to generate the print version. HTTP status: {req.status}')

if __name__ == '__main__':
    run(main())
