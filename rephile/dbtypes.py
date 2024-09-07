#!/usr/bin/env python3
'''
rephile cache types
'''
import os
import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, \
    LargeBinary, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        
class Digest(Base):
    '''
    A hash based digest of some data
    '''
    __tablename__ = "digest"

    # sha256
    id = Column(String, primary_key=True)

    size = Column(Integer)

    mime = Column(String)
    magic = Column(String)

    attrs = relationship("Attribute", backref="digest")
    paths = relationship("Path", backref="digest")
    thumbs = relationship("Thumb", backref="digest")
    
    def tags(self):
        return [x.head for x in self.tag_edges]

    def __repr__(self):
        return "<Digest: %s [%s] %s>" % \
            (self.id[:8], self.mime, self.size)

    def find_attr(self, name):
        for a in self.attrs:
            if name == a.name:
                return a
            

    @property
    def attrmap(self):
        'Attribute list as dictionary'
        am = getattr(self, '_attrmap', None)
        if am: return am
        am = dict()
        for a in self.attrs:
            am[a.name] = a.value
        self._attrmap = am
        return self._attrmap

    @property
    def attr(self):
        'Attribute list as object of attributes'
        ad = getattr(self, '_attrdict', None)
        if ad: return ad
        self._attrdict = AttrDict(self.attrmap)
        return self._attrdict

    def thumb(self, fdsize="normal"):
        for one in self.thumbs:
            if fdsize == one.fdsize:
                return one

class Tag(Base):
    '''
    A node in a tag graph.
    '''
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)

    name = Column(String)        # visible identifier
    description = Column(String) # human readable definition

    __table_args__ = (UniqueConstraint('name', name='_name_uc'),)

    def parents(self):
        return [x.head for x in self.parent_edges]

    def tails(self):
        return [x.tail for x in self.child_edges]

    def digests(self):
        return [x.tail for x in self.digest_edges]

# Putting a graph in SQL may not be performant.
# An alernative is storing all ancestor node IDs in an array.
# https://www.sqlite.org/json1.html

class TagTagEdge(Base):
    '''
    A tag->tag edge.

    children = child_edges.tail(s)
    child -> tail.[child edges].head -> TAG -> tail.[parent eges].head -> parent
    parent = parent_edges.head(s)

    '''
    __tablename__ = "tagtagedge"

    id = Column(Integer, primary_key=True)

    head_id = Column(Integer, ForeignKey("tag.id"), nullable=False)
    tail_id = Column(Integer, ForeignKey("tag.id"), nullable=False)

    tail = relationship(
        Tag, primaryjoin=tail_id == Tag.id, backref="child_edges"
    )

    head = relationship(
        Tag, primaryjoin=head_id == Tag.id, backref="parent_edges"
    )

    __table_args__ = (UniqueConstraint('tail_id', 'head_id'),)

    def __init__(self, tail, head):
        self.tail = tail
        self.head = head


class DigestTagEdge(Base):
    '''
    A digest->tag edge.
    '''
    __tablename__ = "digesttagedge"

    id = Column(Integer, primary_key=True)

    # the "head"
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)
    # the "tail"
    digest_id = Column(Integer, ForeignKey("digest.id"), nullable=False)

    tag = relationship(
        Tag, primaryjoin=tag_id == Tag.id, backref="digest_edges"
    )
    digest = relationship(
        Digest, primaryjoin=digest_id == Digest.id, backref="tag_edgess"
    )

    __table_args__ = (UniqueConstraint('digest_id', 'tag_id'),)

    def __init__(self, digest, tag):
        self.digest = digest
        self.tag = tag


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

    __table_args__ = (UniqueConstraint('digest_id', 'name',
                                       name='_name_uc'),)

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
    # absolute path, but not realpath
    id = Column(String, primary_key=True)
    real = Column(String)
    mode = Column(Integer, default=0)
    uid = Column(Integer, default=-1)
    gid = Column(Integer, default=-1)
    atime = Column(DateTime, default=0)
    mtime = Column(DateTime, default=0)
    ctime = Column(DateTime, default=0)
    digest_id = Column(Integer, ForeignKey("digest.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))

    @property
    def base(self):
        return os.path.basename(self.id)

    @property
    def name(self):
        return os.path.splitext(self.base)[0]

    @property
    def ext(self):
        return os.path.splitext(self.id)[1][1:]

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
