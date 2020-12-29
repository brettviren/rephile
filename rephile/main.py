#!/usr/bin/env python3
'''Main classes and functions for rephile.

Methods of these classes do high level operations.  They deal in
"object level" data and with no concern to UI.

'''
from rephile import db as rdb
import rephile.files
from rephile.jobs import pmapgroup
import rephile.digest

class Rephile:

    def __init__(self, cache, nproc):
        self.cache = cache
        self.nproc = nproc
        
    @property
    def session(self):
        ses = getattr(self, '_session', None)
        if ses: return ses
        self._session = rdb.session(self.cache)
        return self._session

    def exif(self, files):
        'Return EXIF info from files as dict'
        return pmapgroup(rephile.files.exif, files, self.nproc)
        
    def hashsize(self, files):
        'Return (hash,size) tuples for files'
        hss = pmapgroup(rephile.files.hashsize, files, self.nproc)
        ret = list()
        for one in hss:
            ret.append((one['sha256'], one['size']))
        return ret

    def digest(self, paths, force):        
        'Return Digest object matching paths'
        return rephile.digest.bypath(self.session, paths, self.nproc, force)
        
