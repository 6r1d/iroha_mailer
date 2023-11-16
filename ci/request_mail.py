"""
Mailer request utility to be integrated in CI.
"""

from asyncio import run
from totp import gen_otp_from_secret_file
from common_req import perform_mail_request, get_arguments

async def main():
    """
    Load arguments, prepare a one-time pass, perform a request for CI.
    """

    args = get_arguments('mail')
    totp = gen_otp_from_secret_file(args.secret_path)
    await perform_mail_request(args.address, args.data_path, totp)


if __name__ == '__main__':
    run(main())
