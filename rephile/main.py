#!/usr/bin/env python3
'''Main classes and functions for rephile.

Methods of these classes do high level operations.  They deal in
"object level" data and with no concern to UI.

'''
import os
from rephile import db as rdb
from rephile.jobs import pmapgroup
import rephile.files
import rephile.digest
import rephile.tags

class Rephile:

    def __init__(self, cache, nproc=1):
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
        '''
        Return Digest objects matching paths.
        '''
        return rephile.digest.build(self.session, paths, self.nproc, force)
        
    def paths(self, files, force=False):
        '''
        Return Path objects matching files.
        '''
        files = [os.path.abspath(f) for f in files]
        digs = self.digest(files, force)
        shas = [d.id for d in digs]
        return rephile.paths.fresh(self.session, zip(files, shas))
        
    def tags(self, *args, assure=False, **kwds):
        '''Return tag objects matching tag name strings.

        If assure is True or kwds are given all tags will be assured to exist.
        Otherwise, return tags in args.

        '''
        if assure or kwds:
            rephile.tags.add(self.session, *args, **kwds)
            args = list(set(list(args) + list(kwds.keys())))
        return rephile.tags.get(self.session, *args)
