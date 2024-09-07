#!/usr/bin/env python
'''API to tags.

Both digests and tags may have tags.  Tags form a directed graph from tagged to
its tag.

'''

from itertools import product

# fixme: this is for upsert.  One day, maybe something besides sqlite is used.
from sqlalchemy.dialects.sqlite import insert as upsert

from rephile.dbtypes import Tag, Digest, TagTagEdge, DigestTagEdge
from rephile.util import is_sequence

def get(session, *names):
    '''
    Return tags objects with given names.
    '''
    return session.query(Tag).filter(Tag.name.in_(names)).all()

def add(session, *args, **kwds):
    '''Add some tags.

    Tags may be added with just their names (args) or a dict mapping name to
    description (kwds).

    Existing tags which are named in kwds will have their description replaced.

    '''
    if args:
        stmt = upsert(Tag).values([dict(name=n) for n in args])
        stmt = stmt.on_conflict_do_nothing(index_elements=[Tag.name])
        session.execute(stmt)
    if kwds:
        stmt = upsert(Tag).values([dict(name=n, description=d)
                                   for n,d in kwds.items()])
        stmt = stmt.on_conflict_do_update(
            index_elements=[Tag.name],
            set_=dict(description=stmt.excluded.description))
        session.execute(stmt)        
    session.commit()
    
# fixme: this is a dumb name.
def birth(session, parents, children):
    '''
    Make the parents parent of the children.

    Both may be scalar or a sequence.

    Parent elements must be tags objects or tag names.

    Children must be tag objects, tag names or digest objects.
    '''
    if not is_sequence(parents):
        parents = [parents]
    ptags = [p for p in parents if isinstance(p,Tag)]
    pstrs = [p for p in parents if isinstance(p,str)]
    if pstrs:
        ptags += get(session, pstrs)

    if not is_sequence(children):
        children = [children]
    cdigs = [p for p in children if isinstance(p,Digest)]
    ctags = [p for p in children if isinstance(p,Tag)]
    cstrs = [p for p in children if isinstance(p,str)]
    if cstrs:
        ctags += get(session, cstrs)

    tte = [TagTagEdge(c,p) for c,p in product(ctags, ptags)]
    dte = [DigestTagEdge(d,t) for d,t in product(cdigs, ptags)]

    session.add_all(tte + dte)
    session.commit()


