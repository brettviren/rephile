#!/usr/bin/env python3

import imgur_uploader as imup
import urllib

def upload(fname):
    '''
    Upload file name to imgur, return URL
    '''
    # this is basically imgur-uploader's main command
    config = imup.get_config()
    #print(config)
    if not config:
        return
    if "refresh_token" in config:
        client = imup.ImgurClient(config["id"], config["secret"], refresh_token=config["refresh_token"])
        anon = False
        #print ("refreshed token", client)
    else:
        #print ("connect with secret")
        client = imup.ImgurClient(config["id"], config["secret"])
        anon = True

    response = client.upload_from_path(fname, anon=anon)
    return response.get("link", None)
    
