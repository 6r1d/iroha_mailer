# pylint: disable=C0114
from logging import info
from aiohttp import ClientSession
from aiohttp.formdata import FormData

# Messages to display in the log
REQUEST_MESSAGES = {
    'email': {
        200: 'Emails sent successfully',
        'default': 'Unable to send the emails. HTTP status: {status}'
    },
    'print': {
        200: 'The result was generated',
        'default': 'Unable to generate the print version. HTTP status: {status}'
    }
}

async def prepare_request(data_path, totp):
    """
    Prepares the FormData instance with a TOTP key
    for the request.
    """
    data = FormData()
    data.add_field('password', totp)
    with open(data_path, 'rb') as template_data:
        data.add_field('template_data', template_data.read())
    return data

async def log_request(mode, status):
    """
    Log the request result,
    displaying the result and using an appropriate message.
    """
    result = ''
    result = REQUEST_MESSAGES[mode].get(status if status == 200 else 'default')
    result = result.format(status=status)
    info(result)

async def perform_mail_request(addr: str, data_path: str, totp: str):
    """
    Sends a request for mailing.
    """
    async with ClientSession() as session:
        data = await prepare_request(data_path, totp)
        req = await session.post(addr, data=data)
        await log_request('email', req.status)

async def perform_print_request(addr: str, data_path: str, totp: str):
    """
    Sends a request for a print version.
    """
    result = ''
    async with ClientSession() as session:
        data = await prepare_request(data_path, totp)
        req = await session.post(addr, data=data)
        await log_request('print', req.status)
        if req.status == 200:
            result = await req.text()
    return result
