#!/usr/bin/env python3
'''
Low level operations on files.
'''
import os
import io
import magic
import hashlib
from PIL import Image
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



def hashsize_one(fname):
    'Return tuple of hash and size'
    h1 = hashlib.sha256()
    h2 = hashlib.md5()

    fp = open(fname, 'rb')
    data = fp.read()
    size = 0
    while len(data) > 0:
        size += len(data)
        h1.update(data)
        h2.update(data)
        data = fp.read()
    fp.close()
    return dict(sha256=h1.hexdigest(), md5=h2.hexdigest(), size=size)
    
def hashsize(files):
    'Map hashsize_one onto list of files'
    if isinstance(files, str):
        files = [files]
    return [hashsize_one(f) for f in files]

def mime_one(path):
    return magic.from_file(path, mime=True)
def magic_one(path):
    return magic.from_file(path)

def info(files):
    if isinstance(files, str):
        files = [files]
    ret = list()
    for path in files:
        rpath = os.path.realpath(path)
        dat = dict(
            ext=os.path.splitext(path)[1][1:],
            realpath=rpath,
            abspath=os.path.abspath(path),
            magic=magic.from_file(rpath),
            mime=magic.from_file(rpath, mime=True))
        ret.append(dat)
    return ret


def thumb(files, sizes=((128,128), (256,256), (512,512))):
    '''
    Generate thumbnails.  

    Return a list with per-file entries.

    Each entry is a dictionary keyed by size tuple.
    '''
    if isinstance(files, str):
        files = [files]
    ret = list()
    for path in files:
        one = dict()
        full = Image.open(path)
        for size in sizes:
            if size[0] > full.size[0] or size[1] > full.size[1]:
                break
            img = full.copy()
            img.thumbnail(size)
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                dat = output.getvalue()
                one[img.size] = dat
        ret.append(one)
    return ret

