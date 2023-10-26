"""
Internal utilities, not fitting in other packages.
"""

from markdown import markdown

def reformat_input_data(data):
    """
    Returns:
        (dict): a dictionary with 'delivered', 'current_work', 'planned'
                string lists, reformatted from Markdown to HTML.
    """

    if 'delivered' in data:
        data['delivered'] = [markdown(item) for item in data['delivered']]
    else:
        data['delivered'] = []
    if 'current_work' in data:
        data['current_work'] = [markdown(item) for item in data['current_work']]
    else:
        data['current_work'] = []
    if 'planned' in data:
        data['planned'] = [markdown(item) for item in data['planned']]
    else:
        data['planned'] = []
    return data
