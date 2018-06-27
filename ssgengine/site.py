import logging
_log = logging.getLogger('ssgengine.site')
import os.path
from functools import partial
import re

import jinja2

from .filesystem import Directory, File


class Site(object):
    def __init__(self, path):
        self.path = path
        self.tpl = TemplateEngine(os.path.join(path, '_layout'), {})

    def scan(self):
        dirs = {
            'main': {
                'path': self.path,
                'processor': ProcessorChain((
                    (None, partial(set_attrs, {
                        'layout': 'default.html'
                    }),
                    (None, partial(update_from_path, r'(?P<slug>.+?)(?P<ext>\..+)?$')),
                    (partial(match_ext, '.html'), self.tpl.get_metadata),
                )),
            },
            'posts': {
                'path': os.path.join(self.path, '_posts'),
                'processor': ProcessorChain((
                    (None, partial(update_from_path, r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<slug>.+?)(?P<ext>\..+)$')),
                )),
            },
        }

        for key in ['main', 'posts']:
            _log.info('Scanning %s', dirs[key]['path'])
            for f in Directory(dirs[key]['path']):
                _log.info('Found %s', f.path)
                dirs[key]['processor'](f)
                print f

    def generate(self, force=False):
        pass


class TemplateEngine(jinja2.Environment):
    def __init__(self, template_path, global_context):
        jinja2.Environment.__init__(self, loader=jinja2.FileSystemLoader(template_path))
        self.globals.update(global_context)

    def get_metadata(self, f):
        """Parse HTML file for ``{% set metadata = ... %}`` and add it to *f*."""
        for n in self.parse(open(f.fullpath, 'r').read()).body:
            if isinstance(n, jinja2.nodes.Assign) and n.target.name == 'metadata':
                f.update(n.node.as_const())


class Processor(object):
    pass


class ProcessorChain(list):
    def __call__(self, f):
        for (match, processor) in self:
            if match is None or match(f):
                processor(f)

def set_attrs(attrs, f):
    f.update(attrs)

def update_from_path(regex, f):
    """Update *f* by applying *regex* search to *f.path*."""
    metadata = re.search(regex, f.path).groupdict()
    f.update(metadata)

def match_ext(ext, f):
    return 'ext' in f and f['ext'] == ext
