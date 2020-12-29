#!/usr/bin/env python3
'''
Medium level operations on Digest.
'''
from rephile.types import *
from rephile.jobs import pmapgroup
import rephile.files as rfiles


def make_some(dats):
    'Form one Digest from packing. Use instead digest.make(paths)'
    # assure we don't double add
    byhash = dict()
    for dat in dats:
        h1 = dat['sha256']
        if h1 in byhash:
            continue
        dig = Digest(
            sha256 = dat['sha256'],
            md5 = dat['md5'],
            size = dat['size'],
            ext = dat['ext'],
            mime = dat['mime'],
            magic = dat['magic'])
            
        byhash[h1] = dig

    # one more time to retain order
    ret = list()
    for dat in dats:
        ret.append(byhash[dat['sha256']])
    return ret


def make(paths, nproc=1):
    '''
    Unconditionally create Digests corresponding to paths.
    '''
    dat1 = pmapgroup(rfiles.hashsize, paths, nproc)
    dat2 = pmapgroup(rfiles.info, paths, nproc)
    dat = list();
    for d1,d2 in zip(dat1, dat2):
        dat.append(dict(d1, **d2))
    # Do not parallelize on make_some() as the same hash may be
    # created in different groups, leading to violation of UNIQUE
    # constraint.  
    return make_some(dat)


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
    if not new_digs:
        raise ValueError("failed to make new Digests")
    session.add_all(new_digs)
    session.flush()             # to resolve ids

    new_dids = [d.id for d in new_digs]
    pis = zip(new_paths, new_dids)

    pis = list(pis)

    path_objs = rpaths.make(pis, nproc)
    session.bulk_save_objects(path_objs)

    attr_objs = rattrs.make(pis, nproc)
    session.bulk_save_objects(attr_objs)
    session.commit()
    for path, dig in zip(new_paths, new_digs):
        byp[path] = dig
    return [byp.get(p, None) for p in paths]

def asdict(dig):
    '''
    Return Digest info as a dictionary .
    '''
    ret = dict()
    for attr in dig.attrs:
        ret[attr.name] = attr.value()
    ret["sha256"] = dig.sha256
    ret["md5"] = dig.md5
    ret["size"] = dig.size
    ret["ext"] = dig.ext
    ret["mime"] = dig.mime
    ret["magic"] = dig.magic
    ret["paths"] = [p.path for p in dig.paths]
    return ret

def astext(dig, pat):
    '''
    Return a formatted string by applying pat to attributes of dig
    '''
    dat = asdict(dig)
    return pat.format(**dat)

