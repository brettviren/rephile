#!/usr/bin/env python
'''
Tooling for running multiprocessing
'''
import multiprocessing

from .util import chunkify, flatten

def pmap(meth, lst, nproc=1):
    '''
    Call meth on each element of lst.
    '''
    pool = multiprocessing.Pool()
    pool = multiprocessing.Pool(processes=nproc)
    answer = pool.map(meth, lst)
    pool.close()
    return answer

def pmapgroup(meth, lst, nproc):
    '''
    Run meth on groups of elements in lst
    '''
    groups = chunkify(lst, nproc)
    got = pmap(meth, groups, nproc)
    return flatten(got)
