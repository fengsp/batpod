# -*- coding: utf-8 -*-
"""
    This is a example app
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from batpod import BatPod, abort, redirect


app = BatPod(__name__)


@app.route(r'/')
def index(request):
    return 'hello world!'


@app.route(r'/name/(?P<name>\w+)/')
def fsp(request, name):
    return name


@app.route(r'/except/fsp/')
def exceptfsp(request):
    abort(501)


@app.route(r'/redirect/')
def redir(request):
    return redirect('/')


@app.error(404)
def _404():
    return '404 fsp page'


if __name__ == "__main__":
    app.run(debug=True)
