# -*- coding: utf-8 -*-
"""
    batpod.serving
    ~~~~~~~~~~~~~~

    A simple WSGI server with reloader.

    :copyright: (c) 2013 by fsp.
    :license: BSD, see LICENSE for more details.
"""


import os, sys, time
from wsgiref.simple_server import make_server


def _iter_module_files():
    for module in sys.modules.values():
        filename = getattr(module, '__file__', None)
        if filename:
            if filename[-4:] in ('.pyc', '.pyo'):
                filename = filename[:-1]
            yield filename


def _reloader_loop():
    mtimes = {}
    while 1:
        for filename in _iter_module_files():
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue
            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                print ' * Detected change, reloading'
                sys.exit(3)
        time.sleep(1)


def restart_with_reloader():
    import subprocess
    while 1:
        print ' * Restarting with reloader'
        args = [sys.executable] + sys.argv
        new_environ = os.environ.copy()
        new_environ['BATPOD_RELOADER'] = 'true'
        exit_code = subprocess.call(args, env=new_environ)
        if exit_code != 3:
            return


def run_server(host, port, app):
    def inner():
        httpd = make_server(host, port, app)
        httpd.serve_forever()
    if os.environ.get('BATPOD_RELOADER') != 'true':
        print " * Serving on port " + str(port) + "..."
    else:
        try:
            import thread
            thread.start_new_thread(inner, ())
            _reloader_loop()
        except KeyboardInterrupt:
            sys.exit(0)
    try:
        restart_with_reloader()
    except KeyboardInterrupt:
        sys.exit(0)
    sys.exit(0)
