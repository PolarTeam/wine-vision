#! /usr/bin/python
# -*- coding: utf-8 -*-

from winevision import stub

def test_creation():
    p = stub.Stub()
    assert p is not None
    
    p2 = p.random_method()
    assert p2 is not None
    assert isinstance(p2, stub.Stub) 

    p3 = p.random_attribute.r_attribut.method()
    assert p3 is not None
    assert isinstance(p3, stub.Stub) 


def test_attributes():
    p = stub.Stub()
    assert p is not None
    
    p.attr = "a"
    assert p.attr == "a"
