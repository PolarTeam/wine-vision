#! /usr/bin/python
# -*- coding: utf-8 -*-


class Proxy(object):
    def __getattr__(self, *args, **kargs):
        return Proxy()
        
    def __call__(self, *args, **kargs):
        return Proxy()

