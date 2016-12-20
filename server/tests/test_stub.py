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

def test_function():
    p = stub.Stub()
    assert p is not None

    def inner_function(attr1, attr2):
        return attr1, attr2

    p.function = inner_function

    assert inner_function == p.function    
    assert ('a', 'b') == p.function('a', 'b')


def test_method():
    p = stub.Stub()
    assert p is not None

    def inner_method(self, attr1, attr2):
        assert self == p
        return attr1, attr2

    stub.attach_as_method(p, inner_method)

    assert inner_method != p.inner_method 
    assert ('a', 'b') == p.inner_method('a', 'b')
