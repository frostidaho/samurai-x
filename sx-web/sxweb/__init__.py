import os
import wsgiref
from wsgiref import simple_server

import samuraix
from samuraix.plugin import Plugin

from webob import Request, Response
from webob import exc

from mako.template import Template
from mako.lookup import TemplateLookup

import logging
log = logging.getLogger(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

template_lookup = TemplateLookup(
        directories=[template_dir], 
        module_directory='/tmp/mako_modules',
)


def render(templatename, **kwargs):
    template = template_lookup.get_template(templatename)
    return template.render(**kwargs)


class App(object):
    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.environ['REMOTE_ADDR'] != '127.0.0.1':
            resp = exc.HTTPBadRequest(str(e))
        try:
            resp = self.process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def process(self, request):
        return Response(
                content_type="text/html", 
                body=render('index.html'),
        )


class SXWeb(Plugin):

    def __init__(self, app):
        self.app = app
        app.push_handlers(self)

        self.config = samuraix.config.get('sxweb', {})
        self.port = self.config.get('port', 8000)

    def on_ready(self, app):
        log.info('serving on port %s', self.port)
        self.httpd = simple_server.make_server('', self.port, App())
        app.add_fd_handler('read', self.httpd.socket, self.httpd.handle_request)


