#!/usr/bin/env python
'''
Simple interface to the beautifully simple 0x0.st
'''
import requests

url = 'https://0x0.st/'

#url = 'http://localhost:5000'
# see below for local 0x0.st setup

def upload(fname):
    '''
    Upload file to 0x0.st, return file name or None on fail

    curl -F'file=@yourfile.png' https://0x0.st
    '''
    files = {"file": open(fname, 'rb')}
    got = requests.post(url, files=files)
    return got.text



### Setup a local 0x0 instance.
### It sure would have been nice to have this in 0x0's readme!
# git clone https://github.com/mia-0/0x0.git
# cd 0x0 && echo layout python3 > .envrc && direnv allow
# pip install -r requirements.txt
# mkdir instance
# echo 'SQLALCHEMY_DATABASE_URI = "sqlite:///0x0.db"' > instance/config.py
# FLASK_APP=fhost flask db upgrade
# ls -l 0x0.db 
# FLASK_ENV=development FLASK_APP=fhost flask run
# rephile 0x0 something.png
# ls -l up/
