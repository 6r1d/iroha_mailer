"""
This module is used to send mail asynchronously
through an SMTP server using aiosmtplib.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP

async def send_mail_async(sender, to, subject, text, **params):
    """
    Send an outgoing email with the given parameters.

    Arguments:

    sender:
        (str) Who sends the email

    to:
        (str) A recipient email addresses.

    subject:
        (str) The subject of the email.

    text:
        (str) The text of the email.

    text:
        (str) str

    params:
        (dict) An optional set of parameters. (See below)
    """

    # Default Parameters
    cc = params.get("cc", [])
    bcc = params.get("bcc", [])
    mail_params = params.get("mail_params")
    list_unsubscribe = params.get("list_unsubscribe", None)

    # Prepare Message
    msg = MIMEMultipart()
    msg.preamble = subject
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    if len(cc):
        msg['Cc'] = ', '.join(cc)

    if len(bcc):
        msg['Bcc'] = ', '.join(bcc)

    # List-Unsubscribe header
    if list_unsubscribe:
        msg['List-Unsubscribe'] = f'<{list_unsubscribe}>'
    # Read confirmation
    msg['Disposition-Notification-To'] = f'"Iroha News" <{sender}>'
    msg['Return-Receipt-To'] = f'"Iroha News" <{sender}>'

    msg.attach(MIMEText(text, 'html', 'utf-8'))

    # Contact SMTP server and send Message
    host = mail_params.get('host', 'localhost')
    is_ssl = mail_params.get('SSL', False)
    is_tls = mail_params.get('TLS', False)
    port = mail_params.get('port', 465 if is_ssl else 25)
    smtp = SMTP(hostname=host, port=port, use_tls=is_ssl)
    await smtp.connect()
    if is_tls:
        await smtp.starttls()
    if 'user' in mail_params:
        await smtp.login(mail_params['user'], mail_params['password'])
    await smtp.send_message(msg)
    await smtp.quit()
