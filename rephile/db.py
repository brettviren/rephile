#!/usr/bin/env python3
'''Functions that operate on the cache db.'''

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rephile.types import Base

def engine(url):
    'Get db engine'
    if ":" not in url:          # a file
        url = "sqlite:///"+url
    return create_engine(url, echo=False)

def init(url):
    '''
    Initialize a rephile cache.
    '''
    print(f'rephile initialize {url}')
    Base.metadata.create_all(engine(url))

def session(dbfile):
    '''
    Return a DB session
    '''
    if not dbfile:
        raise ValueError("no rephile cache url")
    if not os.path.exists(dbfile):
        init(dbfile)
    if os.stat(dbfile).st_size == 0:
        raise ValueError("rephile cache is not initialized")
    Session = sessionmaker(bind=engine(dbfile))
    return Session()

