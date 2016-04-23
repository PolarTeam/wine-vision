#! /usr/bin/python
# -*- coding: utf-8 -*-


class Proxy(object):
    def __getattribute__(self, *args, **kargs):
        return Proxy()
