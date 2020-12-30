#!/usr/bin/env python3
'''
Medium level operations on Path
'''
import os
from rephile.types import Path
from rephile.jobs import pmapgroup
from datetime import datetime

def make_one(path, did):
    s = os.stat(path)
    p = Path(id=os.path.abspath(path),
             real = os.path.realpath(path),
             ext = os.path.splitext(path)[1][1:],
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
    for path, did in pis:
        p = make_one(path, did)
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


def fresh(session, path_hashes):
    # Make new Paths for any we don't have
    path_hashes = list(path_hashes)
    paths = [ph[0] for ph in path_hashes]

    have_paths = session.query(Path).filter(Path.id.in_(paths)).all()
    have_paths = {p.id:p for p in have_paths}

    ret = list()
    fresh_paths = list()
    for path, sha in path_hashes:
        have = have_paths.get(path, None)
        if have is None:
            have = make_one(path, sha)
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
    import rephile.digest
    ret = dict()
    for column in pobj.__table__.columns:
        ret[column.name] = str(getattr(pobj, column.name))
    ret["digest"] = rephile.digest.asdict(pobj.digest)
    return ret
