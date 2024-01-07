#!/usr/bin/env python3
'''
Medium level operations on Path
'''
import os
from rephile.types import Path
from rephile.jobs import pmapgroup
from datetime import datetime

def make_one(filename, did):
    s = os.stat(filename)
    p = Path(id=os.path.abspath(filename),
             real = os.path.realpath(filename),
             mode = s.st_mode,
             uid = s.st_uid, 
             gid = s.st_gid, 
             atime = datetime.fromtimestamp(s.st_atime),
             mtime = datetime.fromtimestamp(s.st_mtime),
             ctime = datetime.fromtimestamp(s.st_ctime),
             digest_id = did)
    return p

def make_some(pis):
    ret = list()
    for filename, did in pis:
        p = make_one(filename, did)
        ret.append(p)
    return ret

def make(pis, nproc=1):
    return pmapgroup(make_some, pis, nproc)

    
def ids(session, filenames):
    got = session.query(Path.id).filter(Path.path.in_(filenames))
    byp = dict()
    for filename, pid in got.all():
        byp[filename] = pid
    return byp


def fresh(session, fname_hashes):
    '''Make new Paths for any we don't have'''
    fname_hashes = list(fname_hashes)
    fnames = [ph[0] for ph in fname_hashes]

    have_fnames = session.query(Path).filter(Path.id.in_(fnames)).all()
    have_fnames = {p.id:p for p in have_fnames}

    ret = list()
    fresh_paths = list()
    for fname, sha in fname_hashes:
        have = have_fnames.get(fname, None)
        if have is None:
            have = make_one(fname, sha)
            fresh_paths.append(have)
            ret.append(have)
            continue
        ret.append(have)
        if have.digest_id != sha:
            have.digest_id = sha
            fresh_paths.append(have)
    if fresh_paths:
        session.bulk_save_objects(fresh_paths)
    return ret
        

    
def asdict(pobj):
    ret = dict()
    for one in dir(pobj):
        if one.startswith("_"):
            continue
        ret[one] = getattr(pobj,one)

    # for column in pobj.__table__.columns:
    #     ret[column.name] = getattr(pobj, column.name)
    # #ret["digest"] = rephile.digest.asdict(pobj.digest)
    # ret["digest"] = pobj.digest

    return ret
