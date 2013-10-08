# -*- coding: utf-8 -*-
"""
    batpod
    ~~~~~~

    This module implements the central WSGI application object.

    :copyright: (c) 2013 by fsp.
    :license: BSD, see LICENSE for more details.
"""

import urllib
import re


class BatPod(object):

    def __init__(self, import_name):
        self.url_map = {}
        self.error_handler = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.teardown_request_funcs = []

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        res = Response(response)
        return Response(response, start_response)

    def route(self, rule, methods=['GET']):
        def decorator(func):
            self.add_url_rule(methods, rule, func)
            return func
        return decorator

    def error(self, code):
        def decorator(func):
            self.error_handler[code] = func
            return func
        return decorator

    def add_url_rule(self, methods, rule, func):
        if not rule.endswith('/'):
            rule = rule + '/'
        rule_re = re.compile('^%s$' % rule)
        for method in methods:
            self.url_map.setdefault(method, []).append((rule_re, rule, func))

    def before_request(self, func):
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        self.after_request_funcs.append(func)
        return func

    def teardown_request(self, func):
        self.teardown_request_funcs.append(func)
        return func
        
    def dispatch_request(self, request):
        try:
            try:
                for rule_tuple in self.url_map[request.method]:
                    match = rule_tuple[0].search(request.rule)
                    if match is not None:
                        view = rule_tuple[2]
                        return view(request, **match.groupdict())
            except KeyError:
                raise HTTPException(404)
            else:
                raise HTTPException(404)
        except HTTPException, e:
            if e.code in self.error_handler:
                view = self.error_handler[e.code]
                e_response = Response(view())
                e_response.set_status(e.code)
                return e_response
            else:
                return e

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host=None, port=None, debug=False):
        if host is None:
            host = '127.0.0.1'
        if port is None:
            port = 8000
        if debug:
            from exts.serving import run_server
            run_server(host, port, self)
        else:
            from wsgiref.simple_server import make_server
            make_server(host, port, self).serve_forever()
            


class Request(object):

    charset = 'utf-8'
    max_content_length = None

    def __init__(self, environ):
        self.environ = environ

    @property
    def url(self):
        parts = [self.environ['wsgi.url_schema'], '://', self.host]
        parts.append(urllib.quote(self.environ.get('SCRIPT_NAME', '') \
                                              .rstrip('/')))
        parts.append(urllib.quote('/' + self.environ.get('PATH_INFO', '') \
                                                    .lstrip('/')))
        qs = self.environ.get('QUERY_STRING')
        if qs:
            parts.append('?' + qs)
        return ''.join(parts)

    @property
    def rule(self):
        parts = []
        parts.append(urllib.quote(self.environ.get('SCRIPT_NAME', '') \
                                              .rstrip('/')))
        parts.append(urllib.quote('/' + self.environ.get('PATH_INFO', '') \
                                                    .lstrip('/')))
        return ''.join(parts)

    @property
    def args(self):
        from urlparse import parse_qs
        return parse_qs(self.environ.get('QUERY_STRING', ''))

    @property
    def headers(self):
        return self.environ

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def cookies(self):
        from Cookie import SimpleCookie
        cookie = SimpleCookie()
        cookie.load(self.environ.get('HTTP_COOKIE', ''))
        result = {}
        for key, value in cookie.iteritems():
            result[key] = value
        return result

    @property
    def host(self):
        """Return the host"""
        if 'HTTP_X_FORWARDED_HOST' in self.environ:
            return self.environ['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in self.environ:
            return self.environ['HTTP_HOST']
        result = environ['SERVER_NAME']
        if (environ['wsgi.url_schema'], environ['SERVER_ROOT']) not \
            in (('https', '443'), ('http', '80')):
            result += ':' + environ['SERVER_PORT']
        return result

    @property
    def is_xhr(self):
        return self.environ.get('HTTP_X_REQUESTED_WITH', '').lower() \
            == 'xmlhttprequest'

    @property
    def is_secure(self):
        return self.environ['wsgi.url_schema'] == 'https'


class Response(object):
    
    def __init__(self, response, start_response=None):
        self.status = '200 OK'
        self.content_type = 'text/html'
        self.headers = []
        self.body = ''
        
        if isinstance(response, Response):
            self.__dict__ = response.__dict__
        elif isinstance(response, HTTPException):
            self.status = '%d %s' % (response.code, response.name)
            self.body = response.get_error_body()
        else:
            self.body = response
        
        if start_response is not None:
            headers = [('Content-Type', "%s; charset=utf-8" \
                % self.content_type)] + self.headers
            start_response(self.status, headers)

    def add_header(self, key, value):
        self.headers.append((key, value))

    def set_status(self, code):
        self.status = "%d %s" % (code, HTTP_STATUS_CODES[code])

    def __iter__(self):
        for char in self.body:
            yield char


HTTP_STATUS_CODES = {
    100:    'Continue',
    101:    'Switching Protocols',
    102:    'Processing',
    200:    'OK',
    201:    'Created',
    202:    'Accepted',
    203:    'Non Authoritative Information',
    204:    'No Content',
    205:    'Reset Content',
    206:    'Partial Content',
    207:    'Multi Status',
    226:    'IM Used',              # see RFC 3229
    300:    'Multiple Choices',
    301:    'Moved Permanently',
    302:    'Found',
    303:    'See Other',
    304:    'Not Modified',
    305:    'Use Proxy',
    307:    'Temporary Redirect',
    400:    'Bad Request',
    401:    'Unauthorized',
    402:    'Payment Required',     # unused
    403:    'Forbidden',
    404:    'Not Found',
    405:    'Method Not Allowed',
    406:    'Not Acceptable',
    407:    'Proxy Authentication Required',
    408:    'Request Timeout',
    409:    'Conflict',
    410:    'Gone',
    411:    'Length Required',
    412:    'Precondition Failed',
    413:    'Request Entity Too Large',
    414:    'Request URI Too Long',
    415:    'Unsupported Media Type',
    416:    'Requested Range Not Satisfiable',
    417:    'Expectation Failed',
    418:    'I\'m a teapot',        # see RFC 2324
    422:    'Unprocessable Entity',
    423:    'Locked',
    424:    'Failed Dependency',
    426:    'Upgrade Required',
    449:    'Retry With',           # proprietary MS extension
    500:    'Internal Server Error',
    501:    'Not Implemented',
    502:    'Bad Gateway',
    503:    'Service Unavailable',
    504:    'Gateway Timeout',
    505:    'HTTP Version Not Supported',
    507:    'Insufficient Storage',
    510:    'Not Extended'
}


class HTTPException(Exception):
    
    def __init__(self, code):
        self.code = code
        # Yes I don't seperate EXCEPTION_CODES here, you can raise 200, just don't do it!
        if code not in HTTP_STATUS_CODES:
            raise Exception('illegal HTTP status code')
        self.name = HTTP_STATUS_CODES[code]
        super(HTTPException, self).__init__('%d %s' % (self.code, self.name))
    
    def get_error_body(self):
        """Get the HTML body of HTTP Exception."""
        return (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
            '<title>%(code)s</title>\n'
            '<h1>%(name)s</h1>\n'
        ) % {
            'code':  self.code,
            'name':  self.name
        }


def abort(code):
    """A shortcut for HTTP Exception raise"""
    raise HTTPException(code)  
