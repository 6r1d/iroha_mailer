"""
This module is used to send mail asynchronously
through an SMTP server using aiosmtplib.
"""

from email.mime.multipart import MIMEMultipart
from aiosmtplib import SMTP
from aiosmtplib.errors import SMTPException, SMTPConnectError
from errors import SendingError

async def smtp_send(msg: MIMEMultipart, **params):
    """
    Send an outgoing email with the given parameters
    using the SMTP protocol.

    Arguments:

        msg (MIMEMultipart): a message instance
        params (dict): An optional set of parameters
    """
    # Contact SMTP server and send Message
    host = params.get('host', 'localhost')
    is_ssl = params.get('ssl', False)
    is_tls = params.get('tls', False)
    port = params.get('port', 465 if is_ssl else 25)
    # Initialize an SMTP connection
    smtp = SMTP(hostname=host, port=port, use_tls=is_ssl)
    try:
        await smtp.connect()
    except SMTPConnectError as exc:
        raise SendingError('Unable to connect', 'SMTP') from exc
    try:
        if is_tls:
            await smtp.starttls()
        if 'user' in params:
            await smtp.login(params['user'], params['password'])
        # Send a provided MIMEMultipart message
        await smtp.send_message(msg)
    except SMTPException as sending_err:
        raise SendingError(sending_err.message, 'SMTP') from sending_err
    # Close the SMTP connection
    await smtp.quit()
