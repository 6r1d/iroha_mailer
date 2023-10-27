"""
Mail server utility.

Initializes AioHTTP server, connects related plugins,
sets up logging and OTP features.
"""

from logging import basicConfig as basicLoggingConfig, \
                    INFO as LOGGING_INFO, \
                    warning, exception, error
from asyncio import sleep
from aiohttp import web
from aiosmtplib.errors import SMTPException

from address import AddressBook
from sender import send_mail_async
from render import Renderer, decode_template_data
from filesystem import get_code_dir
from formatting import reformat_input_data
from arguments import get_arguments
from config import Config
from totp import gen_otp_from_secret_file

# The location of a code
CODE_DIR = get_code_dir()
# The templates location
PRINT_TEMPLATE_PATH = CODE_DIR / 'templates/print'
MAIL_TEMPLATE_PATH = CODE_DIR / 'templates/mail'
SITE_TEMPLATE_PATH = CODE_DIR / 'templates/site'

async def index(_):
    """
    Renders an index page.

    Returns:

        web.Response: a response with the Index page content
    """
    render_str = await Renderer(SITE_TEMPLATE_PATH).render_template({})
    return web.Response(text=render_str, content_type='text/html')

async def unsubscribe_by_hash(request):
    """
    Unsubscribe from an email by a hash.
    """
    record = await request.app.get('book').pop_key(
        request.match_info.get('hash', ""),
        "hash"
    )
    text = ''
    if record:
        text = await Renderer(
            SITE_TEMPLATE_PATH,
            template_file='unsubscribed_successfully.html'
        ).render_template({'email': record['email']})
    else:
        text = await Renderer(
            SITE_TEMPLATE_PATH,
            template_file='unsubscribed_no_email.html'
        ).render_template({})
    return web.Response(text=text, content_type='text/html')

async def subscribe(request):
    """
    Returns:
        a subscription page
    """
    data = await request.post()
    unique = await request.app.get('book').add_email(data['email'])
    text = ''
    if unique:
        text = await Renderer(
            SITE_TEMPLATE_PATH,
            template_file='subscription_successful.html'
        ).render_template({})
    else:
        text = await Renderer(
            SITE_TEMPLATE_PATH,
            template_file='subscription_repeat.html'
        ).render_template({})
    return web.Response(text=text, content_type='text/html')

async def schedule(request):
    """
    Schedules the emails to be sent for a proper TOTP key.
    """
    data = await request.post()
    template_data = decode_template_data(
        data['template_data'].file.read().decode('utf-8'),
        'email'
    )
    template_data = reformat_input_data(template_data)
    response = None
    # Generate a one-time password
    otp = gen_otp_from_secret_file(request.app.get('secret_path'))
    if data['password'] == otp:
        emails = await request.app.get('book').read_emails()
        for record in emails:
            unsubscribe_url = None
            if request.app['config'].check_list_unsubscribe_mode():
                unsubscribe_url = request.app['config'].get_site_url() + \
                                  '/unsubscribe/hash/' + \
                                  record['hash']
                template_data['unsubscribe_url'] = unsubscribe_url
            mail_str = await Renderer(MAIL_TEMPLATE_PATH).render_template(template_data)
            mail_to = record['email']
            try:
                await send_mail_async(
                    request.app['config'].get_email_from(),
                    mail_to,
                    template_data['title'] + ': ' + template_data['date'],
                    mail_str,
                    mail_params=request.app['config'].get_smtp(),
                    list_unsubscribe=unsubscribe_url
                )
            except SMTPException as smtp_exc:
                exception(smtp_exc)
                error(f'Unable to send mail to {mail_to}')
            await sleep(1)
        response = web.Response(text='Scheduled', status=200)
    else:
        response = web.Response(text='Unable to send emails', status=403)
        warning(f'Incorrect key: {request.remote}')
    return response

async def preview_render(_):
    """
    Returns:
        A page with a preview form.
    """
    text = await Renderer(SITE_TEMPLATE_PATH, template_file='preview.html').render_template({})
    return web.Response(text=text, content_type='text/html')

async def preview_generator(mode: str, data: dict):
    """
    Generates a preview page for the 
    'print' and 'mail' modes.

    Arguments:
        mode (str): print | mail

    Returns:
        (str) rendered template
    """
    tpath = ''
    if mode == 'print':
        tpath = PRINT_TEMPLATE_PATH
    else:
        tpath = MAIL_TEMPLATE_PATH
    template_data = decode_template_data(
        data['template_data'].file.read().decode('utf-8'),
        'print'
    )
    template_data = reformat_input_data(template_data)
    return await Renderer(tpath).render_template(template_data)

async def view_print_render(request):
    """
    Returns:
        a print template render for a user to preview the PDF.
    """
    data = await request.post()
    render_str = await preview_generator('print', data)
    return web.Response(text=render_str, content_type='text/html')

async def view_mail_render(request):
    """
    Returns:
        a mail template render for a user to preview the emails.
    """
    data = await request.post()
    render_str = await preview_generator('mail', data)
    return web.Response(text=render_str, content_type='text/html')

def register_routes(app):
    """
    Register the AioHTTP routes
    """
    app.add_routes([
        web.get('/', index),
        web.get('/unsubscribe/hash/{hash}', unsubscribe_by_hash),
        web.get('/preview', preview_render),
        web.post('/render/print', view_print_render),
        web.post('/render/mail', view_mail_render),
        web.post('/subscribe', subscribe),
        web.post('/schedule', schedule)
    ])

def main():
    """
    Parse config, configure app, start logging,
    register routes, start the server.

    Returns:
        None
    """
    # Get config and arguments
    args = get_arguments()
    config = Config(args.config_path)
    # Initialise the address book
    book = AddressBook(args.emails_path)
    # Initialise the application
    app = web.Application()
    app['book'] = book
    app['config'] = config
    app['secret_path'] = args.secret_path
    # Initialise logging
    basicLoggingConfig(level=LOGGING_INFO)
    # Add application routes
    register_routes(app)
    # Start the server
    web.run_app(app, **config.get_server_options())

if __name__ == '__main__':
    main()
