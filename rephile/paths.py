#!/usr/bin/env python3
'''
Medium level operations on Path
'''
from rephile.types import Path
from rephile.jobs import pmapgroup

def make_some(pis):
    ret = list()
    for path,did in pis:
        p = Path(path=path, digest_id = did)
        ret.append(p)
    return ret

def make(pis, nproc=1):
    return pmapgroup(make_some, pis, nproc)

    
def ids(session, paths):
    got = session.query(Path.path, Path.id).filter(Path.path.in_(paths))
    byp = dict()
    for path, pid in got.all():
        byp[path] = pid
    return byp
