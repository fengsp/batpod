# -*- coding: utf-8 -*-
"""
    batpod.http
    ~~~~~~~~~~~

    HTTP related wrappers and stuff

    :copyright: (c) 2013 by fsp.
    :license: BSD, see LICENSE for more details.
"""
import urllib


class Request(object):

    def __init__(self, environ):
        self.environ = environ

    @property
    def url(self):
        parts = [self.environ['wsgi.url_schema'], '://', self.get_host()]
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

    def get_host(self):
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


class Response(object):
    
    def __init__(self, start_response, response):
        self.start_response = start_response
        self.response = response
        self.respond()

    def respond(self):
        headers = [('Content-type', 'text/html')]
        status = '200 OK'
        self.start_response(status, headers)
        self.body = self.response

    def __iter__(self):
        for char in self.body:
            yield char
