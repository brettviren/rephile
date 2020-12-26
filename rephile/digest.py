#!/usr/bin/env python3
'''
Medium level operations on Digest.
'''
from rephile.types import *
from rephile.jobs import pmapgroup
import rephile.files as rfiles


def make_some(hsemms):
    'Form one Digest from packing. Use instead digest.make(paths)'
    ret = list()
    for hsemm in hsemms:
        (text, size), (ext, magi, mime) = hsemm
        dig = Digest(text=text, size=size,
                     ext=ext, magic=magi, mime=mime)
        ret.append(dig)
    return ret

def make(paths, nproc=1):
    'Create Digests corresponding to paths'
    hs = pmapgroup(rfiles.hashsize, paths, nproc)
    emm = pmapgroup(rfiles.info, paths, nproc)
    return pmapgroup(make_some, zip(hs, emm), nproc)



import rephile.paths as rpaths
import rephile.attrs as rattrs

def bypath(session, paths, nproc=1, force=False):
    '''
    Return Digests associated with paths.  

    Will ingest any that are not known.

    If force is True, force a cache update.
    '''
    byp = dict()

    if not force:
        have = session.query(Path).filter(Path.path.in_(paths))
        for path in have.all():
            byp[path.path] = path.digest

    new_paths = [p for p in paths if p not in byp]
    if not new_paths:
        return [byp.get(p) for p in paths]

    new_digs = make(new_paths, nproc)
    session.add_all(new_digs)
    session.flush()             # to resolve ids

    new_dids = [d.id for d in new_digs]
    pis = zip(new_paths, new_dids)
    path_objs = rpaths.make(pis, nproc)
    session.bulk_save_objects(path_objs)
    pis = zip(new_paths, new_dids)
    attr_objs = rattrs.make(pis, nproc)
    session.bulk_save_objects(attr_objs)
    session.commit()
    for path, dig in zip(new_paths, new_digs):
        byp[path] = dig
    return [byp.get(p, None) for p in paths]
