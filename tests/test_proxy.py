#! /usr/bin/python
# -*- coding: utf-8 -*-

from winevision import proxy

def test_creation():
    p = proxy.Proxy()
    assert p is not None
    
    p2 = p.random_method()
    assert p2 is not None
    assert isinstance(p2, proxy.Proxy) 

def test_attributes():
    pass
