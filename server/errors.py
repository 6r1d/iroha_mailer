"""
This module provides the errors used by the Iroha news mailing server.
"""

class SendingError(Exception):
    """
    A common exception to inherit other exceptions from.
    """

    def __init__(self, message, protocol):
        super().__init__(message)
        self.protocol = protocol

class GmailAPICredentialsError(Exception):
    """
    An exception called for invalid credentials.
    """

    def __init__(self, message):
        super().__init__(message)

class GmailAPITokenRefreshError(Exception):
    """
    An exception called when token can't be refreshed.
    """

    def __init__(self, message):
        super().__init__(message)
