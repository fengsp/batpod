# -*- coding: utf-8 -*-
"""
    batpod.app
    ~~~~~~~~~~

    This module implements the central WSGI application object.

    :copyright: (c) 2013 by fsp.
    :license: BSD, see LICENSE for more details.
"""


from .serving import run_server
from .http import Request, Response


class BatPod(object):
    """This is the main class"""

    def __init__(self, import_name):
        self.url_map = {}

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return Response(start_response, response)

    def route(self, rule):
        def decorator(func):
            self.add_url_rule(rule, func)
            return func
        return decorator

    def add_url_rule(self, rule, func):
        self.url_map[rule] = func   
        
    def dispatch_request(self, request):
        rule = request.rule
        view = self.url_map[rule]
        return view()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host=None, port=None):
        if host is None:
            host = '127.0.0.1'
        if port is None:
            port = 8000
        run_server(host, port, self)   
