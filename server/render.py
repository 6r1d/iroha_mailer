"""
Internal template code with the async support.
"""

from jinja2 import Template
from jinja2 import FileSystemLoader, Environment
from filesystem import get_code_dir
from tomllib import loads

def decode_template_data(input: str, mode: str):
    data = loads(input)
    data['mode'] = mode
    return data

class Renderer:

    def __init__(self, template_path:str, template_file:str='index.html'):
        self.template_path = template_path
        self.template_file = template_file

    async def prepare_template(self):
        templateLoader = FileSystemLoader(searchpath=self.template_path)
        templateEnv = Environment(loader=templateLoader, enable_async=True)
        template = templateEnv.get_template(self.template_file)
        return template

    async def render_template(self, template_data):
        page_template = await self.prepare_template()
        rendered_template = await page_template.render_async(template_data)
        return rendered_template
