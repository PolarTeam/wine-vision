#! /usr/bin/python
# -*- coding: utf-8 -*-

import types

"""
A stub class that always return a stub object if no attribute is defined

A stub object is also a callable that return a stub object.

"""

class Stub(object):
    def __getattr__(self, *args, **kargs):
        return Stub()
        
    def __call__(self, *args, **kargs):
        return Stub()

def attach_as_method(stub, meth):
    setattr(stub, meth.__name__, types.MethodType(meth, stub))
