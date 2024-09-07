#!/usr/bin/env python3
'''
Medium-level operations on thumbs
'''

from rephile.dbtypes import Thumb
from rephile.jobs import pmapgroup
from rephile.files import thumb as gen_thumbs


def make_some(pis):
    '''
    Make some thumbnails from a zip of (path,digest ID)
    '''
    paths = [pi[0] for pi in pis]
    thumbs = gen_thumbs(paths)
    ret = list()
    for pi, thumbbysize in zip(pis, thumbs):
        path, did = pi
        for size, data in thumbbysize.items():
            trow = Thumb(width=size[0], height=size[1],
                         image=data, digest_id=did)
            ret.append(trow)
    return ret


def make(pis, nproc=1):
    return pmapgroup(make_some, pis, nproc)
