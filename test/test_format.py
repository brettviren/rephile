#!/usr/bin/env python3
import os
import os.path

base = os.path.basename

def test_format_map():

    class C:
        x=42
        y="hi"
        z="foo.bar"

    a=1
    b=2
    c=C()
    print (f"{a} {b} {c.x} {base(c.z)}")
    s="{a} {b} {c.x} {base(c.z)}"

    dat = dict(globals(), **locals())

    print (s.format(**dat))
