"""
Print version request utility to be integrated in CI.
"""

from asyncio import run
from totp import gen_otp_from_secret_file
from common_req import perform_print_request, get_arguments

async def main():
    """
    Load arguments, prepare a one-time pass, perform a request for CI.
    """

    args = get_arguments('print')
    totp = gen_otp_from_secret_file(args.secret_path)
    html_render_str = await perform_print_request(
        args.address, args.data_path, totp
    )
    with open(args.output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(html_render_str)

if __name__ == '__main__':
    run(main())
