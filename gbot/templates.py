from jinja2 import Environment, FileSystemLoader, StrictUndefined
from gbot.util import split_by

env = Environment(loader = FileSystemLoader('./templates'), undefined = StrictUndefined,
                  trim_blocks = True)

def render(template_name, **kwargs):
    return env.get_template(template_name).render(**kwargs).replace('\\\n', '')

def render_lines(template_name, line_length = 10000, **kwargs):
    return [l for _l in render(template_name, **kwargs).splitlines()
            for l in split_by(_l, line_length) if _l.strip()]