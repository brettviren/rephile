#!/usr/bin/env python
'''
Generic utility
'''
from math import ceil
import collections.abc

def chunkify(things, nchunks):
    'Return nchunks-long-sequence of lists of things'
    things = list(things)
    nthings = len(things)
    if not nthings:
        raise ValueError("chunk needs things")
    nper = ceil(nthings/nchunks)
    for ind in range(0, len(things), nper):  
        yield things[ind:ind + nper] 

def flatten(chunks):
    'Return flat list from list of lists'
    return [y for x in chunks for y in x]
    
def is_sequence(obj):
    '''
    Return True if obj is sequence but not string.
    '''
    if isinstance(obj, (str, bytes)): return true
    return isinstance(obj, collections.abc.Sequence)
