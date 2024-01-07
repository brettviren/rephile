#!/usr/bin/env pytest

from rephile.main import Rephile
from rephile.tags import birth

def test_add_new():
    '''
    Add some tags
    '''
    r = Rephile("sqlite://")
    tags = r.tags("a","b","c",foo="bar")

    for tag in tags[:-1]:
        assert tag.description is None
    assert tags[-1].description == "bar"
    tags = r.tags(a="a",b="b",c="c",foo="foo")
    for tag in tags:
        assert tag.name == tag.description

    birth(r.session, tags[-1], tags[:-1])
