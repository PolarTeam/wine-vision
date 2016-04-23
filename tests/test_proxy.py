#! /usr/bin/python
# -*- coding: utf-8 -*-

from winevision import proxy

def test_creation():
    p = proxy.Proxy()
    assert p is not None
    
    p2 = p.random_method()
    assert p2 is not None
    assert isinstance(p2, proxy.Proxy) 

    p3 = p.random_attribute.r_attribut.method()
    assert p3 is not None
    assert isinstance(p3, proxy.Proxy) 


def test_attributes():
    p = proxy.Proxy()
    assert p is not None
    
    p.attr = "a"
    assert p.attr == "a"
