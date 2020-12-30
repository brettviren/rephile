#!/usr/bin/env python3
'''
rephile cache types
'''
from collections import defaultdict
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

import enum
class HashType(enum.Enum):
    md5 = 0
    sha1 = 1
    sha256 = 2
    annex = 3

class Digest(Base):
    '''
    A hash based digest of some data
    '''
    __tablename__ = "digest"
    id = Column(Integer, primary_key=True)

    # git-annex
    sha256 = Column(String, unique=True)
    # thumbnails
    md5 = Column(String, unique=True)

    size = Column(Integer)

    mime = Column(String)
    magic = Column(String)

    attrs = relationship("Attribute", backref="digest")
    paths = relationship("Path", backref="digest")
    thumbs = relationship("Thumb", backref="digest")
    
    def __repr__(self):
        return "<Digest: %s [%s] %s>" % \
            (self.sha256[:8], self.mime, self.size)

    @property
    def attrmap(self):
        am = getattr(self, '_attrmap', None)
        if am: return am
        am = defaultdict(list)
        for a in self.attrs:
            am[a.name].append(a.value)
        self._attrmap = am
        return self._attrmap

    def thumb(self, fdsize="normal"):
        for one in self.thumbs:
            if fdsize == one.fdsize:
                return one

class AttrType(enum.Enum):
    string = 0
    integer = 1
    rational = 2

    def cast(self, value):
        meth = [str,int,float][self.value]
        return meth(value)
    
class Attribute(Base):
    '''
    Metadata associated to some data through a digest.
    '''
    __tablename__ = "attribute"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    atype = Column(Enum(AttrType))
    digest_id = Column(Integer, ForeignKey('digest.id'),
                       nullable=False)

    @property
    def value(self):
        return self.atype.cast(self.text)

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
    path = Column(String, unique=True)
    digest_id = Column(Integer, ForeignKey("digest.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))

class Thumb(Base):
    '''
    Thumbnail image information associated with one digest
    '''
    __tablename__ = "thumb"
    id = Column(Integer, primary_key=True)
    digest_id = Column(Integer, ForeignKey("digest.id"))
    width = Column(Integer)
    height = Column(Integer)
    image = Column(LargeBinary) # PNG binary

    @property
    def fdsize(self):
        'Freedesktop size label'
        if self.width == 0 or self.height == 0:
            return "fail"
        if self.width <= 128 and self.height <= 128:
            return "normal"
        if self.width <= 256 and self.height <= 256:
            return "large"
        if self.width <= 512 and self.height <= 512:
            return "x-large"
        if self.width <= 1024 and self.height <= 1024:
            return "xx-large"
        return "xxx-large"      # not a freedesktop standard
        
    def encode(self):           # future: add arg to set encoding
        import base64
        return base64.b64encode(self.image)
    def htmldata(self):
        return "data:image/png;base64," + self.encode().decode()
