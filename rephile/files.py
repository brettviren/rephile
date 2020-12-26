#!/usr/bin/env python3
'''
Low level operations on files.
'''
import os
import magic
import hashlib

from subprocess import run
import json

def exif(files):
    '''
    Return EXIF of files as array of dicts by running "exiftool".

    Order of input is retained on output.  

    If "files" is a scalar, it's considered a list of one.
    '''
    if not files:
        return ()
    if isinstance(files, str):
        files = [files]
    else:
        files=list(files)
    cmd = ["exiftool", "-j"] + files
    out = run(cmd, capture_output=True)
    text = out.stdout.decode()
    return json.loads(text)


# canonical hasher
Hasher = hashlib.sha256

def hashsize_one(fname):
    'Return tuple of hash and size'
    hasher = Hasher()
    fp = open(fname, 'rb')
    data = fp.read()
    size = 0
    while len(data) > 0:
        size += len(data)
        hasher.update(data)
        data = fp.read()
    fp.close()
    return (hasher.hexdigest(), size)
    
def hashsize(files):
    'Map hashsize_one onto list of files'
    if isinstance(files, str):
        files = [files]
    return [hashsize_one(f) for f in files]

def info(files):
    if isinstance(files, str):
        files = [files]
    ret = list()
    for path in files:
        ext = os.path.splitext(path)[1][1:]
        rpath = os.path.realpath(path)
        magi = magic.from_file(rpath)
        mime = magic.from_file(rpath, mime=True)
        ret.append((ext, magi, mime))
    return ret
