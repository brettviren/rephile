#!/usr/bin/env python3
'''
Medium level operations on Digest.
'''
from rephile.types import *
from rephile.jobs import pmapgroup
import rephile.files as rfiles


def make_one(path):
    'Return Digest of file at path'
    hhs = rfiles.hashsize_one(path)
    return Digest(
        sha256 = hhs['sha256'],
        md5 = hhs['md5'],
        size = hss['size'],
        mime = rfiles.mime(path),
        magic = rfiles.magic(path))
        

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

def build(session, paths, nproc=1, force=False):
    '''
    Return Digests associated with paths.  

    Will ingest any that are not known.

    If force is True, force a cache update for existing digests.
    '''

    # probably there is a more SQL'y way to do the following!

    # the paths may:
    # - be already added
    # - not added but point to existing digs
    # - not added but require new digs

    ptod = dict()                # digs by path
    htod = dict()                # digs by hash
    htop = dict()                # to path from hash

    have_paths = session.query(Path).filter(Path.path.in_(paths))
    for hpath in have_paths.all():
        dig = hpath.digest
        htod[dig.sha256] = dig
        for p in dig.paths:
            ptod[p.path] = dig

    fresh_paths = [p for p in paths if p not in ptod]
    if not fresh_paths:         # done
        return [ptod[p] for p in paths]

    fresh_digs = list()
    for path, one in zip(paths, pmapgroup(rfiles.hashsize, fresh_paths, nproc)):
        htext = one['sha256']
        have = htod.get(htext, None)
        if have:
            ptod[path] = have
            continue
        d = Digest(
            sha256 = htext,
            md5 = one['md5'],
            size = one['size'],
            mime = rfiles.mime_one(path),
            magic = rfiles.magic_one(path))
        ptod[path] = d
        htod[htext] = d
        htop[htext] = path
        fresh_digs.append(d)

    if fresh_digs:
        session.add_all(fresh_digs)
        session.flush()             # to resolve fresh ids

    print ("FRESH PATHS:",fresh_paths)
    pis = [(p,ptod[p].id) for p in fresh_paths]
    path_objs = rpaths.make(pis, nproc)
    session.bulk_save_objects(path_objs)

    pis = [(htop[d.sha256], d.id) for d in fresh_digs]
    attr_objs = rattrs.make(pis, nproc)
    session.bulk_save_objects(attr_objs)
    thumb_objs = rthumbs.make(pis, nproc)
    session.bulk_save_objects(thumb_objs)

    session.commit()

    return [ptod[p] for p in paths]


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

