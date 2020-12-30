#!/usr/bin/env python3
'''Main classes and functions for rephile.

Methods of these classes do high level operations.  They deal in
"object level" data and with no concern to UI.

'''
import os
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

    def init(self):
        'Explicitly initialize the database'
        rdb.init(self.cache)

    def exif(self, files):
        'Return EXIF info from files as dict'
        return pmapgroup(rephile.files.exif, files, self.nproc)
        
    def hashsize(self, files):
        'Return (hash,size) tuples for files'
        hss = pmapgroup(rephile.files.hashsize, files, self.nproc)
        return hss

    def digest(self, paths, force=False):        
        'Return Digest object matching paths'
        return rephile.digest.build(self.session, paths, self.nproc, force)
        
    def paths(self, files, force=False):
        files = [os.path.abspath(f) for f in files]
        digs = self.digest(files, force)
        shas = [d.id for d in digs]
        return rephile.paths.fresh(self.session, zip(files, shas))
        
