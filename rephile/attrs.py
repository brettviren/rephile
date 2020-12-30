#!/usr/bin/env python3
'''
Medium level operations on Attribute
'''
from rephile.types import Attribute, AttrType
from rephile.jobs import pmapgroup
from rephile.files import exif

def make_some(pis):
    '''
    Make some attributes from a zip of (path,digest ID)
    '''
    paths = [pi[0] for pi in pis]
    mds = exif(paths)
    ret = list()
    for pi, md in zip(pis, mds):
        path, did = pi
        for key,val in md.items():
            if type(val) == int:
                atype = AttrType.integer
            elif type(val) == float:
                atype = AttrType.rational
            else:
                atype = AttrType.string
            attr = Attribute(name=key, text=str(val), atype=atype,
                             digest_id = did)
            ret.append(attr)
    return ret


def make(pis, nproc=1):
    return pmapgroup(make_some, pis, nproc)


    
