#!/usr/bin/env python3
'''
rephile cache types
'''

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

import enum
class HashType(enum.Enum):
    md5 = 0
    sha1 = 1
    sha256 = 2
    annex = 3

class AttrType(enum.Enum):
    string = 0
    integer = 1
    rational = 2
    
class Digest(Base):
    '''
    A hash based digest of some data
    '''
    __tablename__ = "digest"
    id = Column(Integer, primary_key=True)

    text = Column(String)
    size = Column(Integer)

    ext = Column(String)
    mime = Column(String)
    magic = Column(String)

    attrs = relationship("Attribute", backref="digest")
    paths = relationship("Path", backref="digest")
    
    def __repr__(self):
        return "<Digest: %s %s .%s [%s]>" % \
            (self.size, self.text, self.ext, self.mime)


class Attribute(Base):
    '''
    Metadata associated to some data through a digest.
    '''
    __tablename__ = "attribute"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    atype = Column(Enum(AttrType))
    digest_id = Column(Integer, ForeignKey('digest.id'))

class Collection(Base):
    '''
    A collection of paths.
    '''
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)    
    name = Column(String)
    host = Column(String)
    base = Column(String)
    paths = relationship("Path", backref="collection")
    # null if simple directory
    annex_id = Column(Integer, ForeignKey("annex.id"))

class Annex(Base):
    '''
    A git-annex
    '''
    __tablename__ = "annex"
    id = Column(Integer, primary_key=True)
    uuid = Column(String)

class Path(Base):
    __tablename__ = "path"
    id = Column(Integer, primary_key=True)
    path = Column(String)
    digest_id = Column(Integer, ForeignKey("digest.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))
