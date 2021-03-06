#!/usr/bin/env python3
'''
Interface to Jinja template rendering
'''

# taken from moo.templates....

import os
from jinja2 import meta, Environment, FileSystemLoader

styles = dict(
    normal=dict(),
    latex=dict(comment_start_string='~{#',
               comment_end_string='#}~',
               block_start_string='~{',
               block_end_string='}~',
               variable_start_string='~{{',
               variable_end_string='}}~')
)


def get_style(filename):
    'Return the markup style to use for a template file'
    style = "normal"
    if '.tex' in filename:
        style = "latex"
    return styles[style]


def make_env(path):
    'Create and return Jinja environment for template at path'
    env = Environment(loader=FileSystemLoader(path),
                      trim_blocks=True,
                      lstrip_blocks=True,
                      extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
                      **get_style(path))
    # env.filters["listify"] = listify
    # env.filters["relpath"] = relpath
    env.globals.update()
    return env


def render(template, params):
    'Render template against dictionary of parameters'
    path = os.path.dirname(os.path.realpath(template))
    env = make_env(path)
    tmpl = env.get_template(os.path.basename(template))
    return tmpl.render(**params)


def imports(template, tpath=None):
    'Return all files imported by template'
    path = os.path.dirname(os.path.realpath(template))
    env = make_env(path)
    ast = env.parse(open(template, 'rb').read().decode())
    subs = meta.find_referenced_templates(ast)
    return [os.path.join(path, one) for one in subs]
