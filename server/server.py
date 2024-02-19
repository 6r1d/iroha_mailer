#!/usr/local/bin/python

"""
Mail server utility.

Initializes AioHTTP server, connects related plugins,
sets up logging and OTP features.
"""

from logging import basicConfig as basicLoggingConfig, \
                    INFO as LOGGING_INFO, \
                    warning
from asyncio import create_task, run, gather
from pathlib import Path

from aiohttp import web
from address import AddressBook
from render import Renderer, decode_template_data
from filesystem import get_code_dir
from formatting import reformat_input_data
from arguments import get_arguments
from config import Config
from totp import validate_otp, gen_otp_from_secret_file
from rotation import queue_email_rotation, Rotator

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
    email = await request.app.get('book').pop_hash(
        request.match_info.get('hash', "")
    )
    text = ''
    if email:
        text = await Renderer(
            SITE_TEMPLATE_PATH,
            template_file='unsubscribed_successfully.html'
        ).render_template({'email': email})
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

async def prepare_email(template_data: dict, sender: str, recipient: str):
    """
    Prepares an email message to be scheduled for sending.
    """
    scheduled_email = {
        'text': await Renderer(MAIL_TEMPLATE_PATH).render_template(template_data),
        'subject': template_data['title'] + ': ' + template_data['date'],
        'sender': sender,
        'recipient': recipient,
        'unsubscribe_url': template_data.get('unsubscribe_url', None)
    }
    return scheduled_email

async def schedule(request):
    """
    Schedules the emails to be sent for a proper TOTP key.
    """
    data = await request.post()
    template_data = decode_template_data(
        data['template_data'].file.read().decode('utf-8')
    )
    template_data = reformat_input_data(template_data)
    # Retrieve the config
    config = request.app['config']
    response = None
    # Generate a one-time password
    otp = gen_otp_from_secret_file(request.app.get('secret_path'))
    # Retrieve the reused configuration parameters
    site_url = config.get_site_url()
    sender = config.get_email_from()
    if data.get('password') == otp:
        emails = await request.app.get('book').read_emails()
        for mail_hash, email in emails.items():
            # Check if if "list-unsubscribe" header is enabled
            if config.check_unsubscription_enabled():
                template_data['unsubscribe_url'] = f'{site_url}/unsubscribe/hash/{mail_hash}'
            # Prepare and queue an email
            scheduled_email = await prepare_email(
                template_data, sender, email
            )
            queue_email_rotation(request.app.get('rotation_path'), scheduled_email)
        response = web.Response(text='Scheduled', status=200)
    else:
        response = web.Response(text='Unable to send emails', status=403)
        warning(f'Incorrect key: {request.remote}')
    return response

async def generate_print(request):
    """
    Generates a print template provided a proper TOTP key.
    """
    data = await request.post()
    template_data = decode_template_data(
        data['template_data'].file.read().decode('utf-8')
    )
    template_data = reformat_input_data(template_data)
    response = None
    # Compare the OTP, render data if it's the same,
    # show an error otherwise
    if validate_otp(request.app.get('secret_path'), data.get('password')):
        render_str = await Renderer(PRINT_TEMPLATE_PATH).render_template(template_data)
        response = web.Response(text=render_str, status=200)
    else:
        response = web.Response(text='Unable to generate the text', status=403)
        warning(f'Incorrect key: {request.remote}')
    return response

class MailerServer:

    """
    The aiohttp-based server class used by mailer.
    """

    def __init__(self, args, config):
        self.running = True
        # Create the aiohttp application instance
        self.app = web.Application()
        self.args = args
        self.config = config
        # Configure app
        self.register_app_parameters()
        self.register_routes()

    def register_app_parameters(self):
        """
        Set up app parameters: address book instance,
        configuration interface, path to secrets,
        a path to the rotation directory
        """
        self.app['book'] = AddressBook(self.args.emails_path)
        self.app['config'] = self.config
        self.app['secret_path'] = self.args.secret_path
        self.app['rotation_path'] = Path(self.args.rotation_path).absolute()

    def register_routes(self):
        """
        Register the AioHTTP routes.
        """
        self.app.add_routes([
            web.get('/', index),
            web.get('/unsubscribe/hash/{hash}', unsubscribe_by_hash),
            web.post('/subscribe', subscribe),
            web.post('/generate_print', generate_print),
            web.post('/schedule', schedule)
        ])

    async def setup_app(self):
        """
        Returns:
            self
        """
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            self.config.get_server_host(),
            self.config.get_server_port()
        )
        await site.start()
        return self

async def main():
    """
    Parse config, configure app, start logging,
    register routes, start the server.

    Returns:
        None
    """
    # Get config and arguments
    args = get_arguments()
    config = Config(args.config_path)
    # Initialise logging
    basicLoggingConfig(level=LOGGING_INFO)
    # Set up the mailer server
    server_instance = MailerServer(args, config)
    # Configure the server
    http_server = create_task(server_instance.setup_app())
    # Configure the rotator
    rotator = Rotator(args.rotation_path, config)
    rotator_task = create_task(rotator.rotate(server_instance, 1))
    # Gather all AsyncIO runners
    return await gather(http_server, rotator_task)

if __name__ == '__main__':
    run(main())
