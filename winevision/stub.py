#! /usr/bin/python
# -*- coding: utf-8 -*-


class Stub(object):
    def __getattr__(self, *args, **kargs):
        return Stub()
        
    def __call__(self, *args, **kargs):
        return Stub()

