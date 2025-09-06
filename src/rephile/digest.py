#!/usr/bin/env python3
'''
Medium level operations on Digest.
'''
import os
from rephile.dbtypes import *
from rephile.jobs import pmapgroup
import rephile.files as rfiles


def make_one(path, sha=None):
    'Return Digest given a current path'
    if sha is None:
        sha, size = rfiles.hashsize_one(path)
    else:
        size = os.stat(path).st_size
    dig = Digest(
        id = sha,
        size = size,
        mime = rfiles.mime_one(path),
        magic = rfiles.magic_one(path))
        
    return dig


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
        d = dict(d1, **d2)
        dat.append(d)
        
    # Do not parallelize on make_some() as the same hash may be
    # created in different groups, leading to violation of UNIQUE
    # constraint.  
    return make_some(dat)


import rephile.paths as rpaths
import rephile.attrs as rattrs
import rephile.thumbs as rthumbs

def fresh(session, paths, nproc=1):
    '''
    Return array of Digests corresponding to paths
    '''
    path_hss = pmapgroup(rfiles.hashsize, paths, nproc)
    ptoh = dict()
    htop = dict()
    htos = dict()
    for path, hs in zip(paths, path_hss):
        sha = hs[0]
        ptoh[path] = sha
        htop[sha] = path
        htos[sha] = hs[1]

    have_digs = session.query(Digest).filter(Digest.id.in_(htop)).all()
    htod = {d.id:d for d in have_digs}
    fresh_objs = list()
    for sha, path in htop.items():
        if sha in htod:
            continue

        # New Digest
        dig = make_one(path, sha)
        htod[sha] = dig
        fresh_objs.append(dig)

        # Attribute and Thumb are based on content
        attrs = rattrs.make_some([(path, sha)])
        fresh_objs += attrs
        thumbs = rthumbs.make_some([(path, sha)])
        fresh_objs += thumbs

    if fresh_objs:
        session.add_all(fresh_objs)
        session.flush()             # to resolve fresh ids

    order = [htod[ptoh[p]] for p in paths]
    return order

def build(session, paths, nproc=1, force=False):
    '''
    Return Digests associated with paths.  

    Will ingest any that are not known.

    If force is True, force a cache update for existing digests.
    '''
    paths = [os.path.abspath(p) for p in paths]
    digs = fresh(session, paths, nproc)
    shas = [d.id for d in digs]
    got = rpaths.fresh(session, zip(paths, shas))
    session.commit()

    return digs


def asdict(dig):
    '''
    Return Digest info as a dictionary .
    '''
    ret = dict()
    for column in dig.__table__.columns:
        ret[column.name] = str(getattr(dig, column.name))
    return ret
    # ret = dict()
    # for attr in dig.attrs:
    #     ret[attr.name] = attr.value
    # ret["hash"] = dig.id
    # ret["size"] = dig.size
    # ret["mime"] = dig.mime
    # ret["magic"] = dig.magic
    # ret["paths"] = [p.id for p in dig.paths]
    # ret["bases"] = [os.path.basename(p) for p in ret["paths"]]
    # return ret

def astext(dig, pat):
    '''
    Return a formatted string by applying pat to attributes of dig
    '''
    dat = asdict(dig)
    return pat.format(**dat)

