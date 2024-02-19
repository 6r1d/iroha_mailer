"""
This module is used to configure a MIMEMultipart message
with all of its details.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

async def configure_multipart(**params) -> MIMEMultipart:
    """
    Configure a MIMEMultipart message

    Arguments:

        params (dict): The MIMEMultipart parameters
                       useful for the task.
    """
    # Retrieve the message subject and sender
    subject: str = params.get('subject', "")
    sender = params.get('sender', "")
    # Prepare Message
    msg = MIMEMultipart()
    msg.preamble = subject
    # Set the source, subject and destination of an email
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = params.get('to', "")
    # Set up "carbon copy", so that everyone receiving the letter
    # sees others
    cc = params.get('cc', [])
    if len(cc):
        msg['Cc'] = ', '.join(cc)
    # Set up "blind carbon copy", so that the ones receiving an email
    # see only themselves among the recepients
    bcc = params.get("bcc", [])
    if len(bcc):
        msg['Bcc'] = ', '.join(bcc)
    # Add a "List-Unsubscribe" header to manage the subscriptions
    list_unsubscribe = params.get('list_unsubscribe', None)
    if list_unsubscribe:
        msg['List-Unsubscribe'] = f'<{list_unsubscribe}>'
    # Configure the reading confirmation
    msg['Disposition-Notification-To'] = f'"Iroha News" <{sender}>'
    msg['Return-Receipt-To'] = f'"Iroha News" <{sender}>'
    # Attach the HTML message content
    msg.attach(MIMEText(params.get('text'), 'html', 'utf-8'))
    return msg
