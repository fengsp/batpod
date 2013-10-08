# -*- coding: utf-8 -*-
"""
    batpod.utils
    ~~~~~~~~~~~~

    Utils

    :copyright: (c) 2013 by fsp.
    :license: BSD, see LICENSE for more details.
"""


class cached_property(object):
    
    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, None)
        if value is  None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
