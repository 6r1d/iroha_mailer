"""
Internal template code with the async support.
"""

from tomllib import loads
from jinja2 import FileSystemLoader, Environment

def decode_template_data(serialized: str, mode: str):
    """
    Deserialize and update the template data.

    TODO:
        refactor
    """
    data = loads(serialized)
    data['mode'] = mode
    return data

# There's no reason to show a PyLint warning as
# I know I want to refactor it.
# pylint: disable=R0903
class Renderer:
    """
    A common rendering utility class.
    Used for both site and e-mail templates.

    TODO:
        introduce the template caching for the site templates
    """

    def __init__(self, template_path:str, template_file:str='index.html'):
        """
        Configure the internal paths
        """
        self.template_path = template_path
        self.template_file = template_file

    async def render_template(self, template_data: dict):
        """
        Load and render a template using the provided data.
        """
        template_loader = FileSystemLoader(searchpath=self.template_path)
        template_env = Environment(loader=template_loader, enable_async=True)
        page_template = template_env.get_template(self.template_file)
        rendered_template = await page_template.render_async(template_data)
        return rendered_template
