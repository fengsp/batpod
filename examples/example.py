# -*- coding: utf-8 -*-
"""
    This is a example app
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from batpod import BatPod


app = BatPod(__name__)


@app.route('/')
def index():
    return 'hello world!'


if __name__ == "__main__":
    app.run()
