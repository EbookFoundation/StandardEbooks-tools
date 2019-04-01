import sys
import os
import xml.etree.ElementTree as ET 
import urllib.request
import json
import se
from dotenv import load_dotenv

POST_URL = "http://ec2-18-219-223-27.us-east-2.compute.amazonaws.com/api/publish"

# Retrieve key and secret from environment variables
def get_credentials():
    load_dotenv() # load environment variables from .env file if it exists

    if "ROE_KEY" not in os.environ or "ROE_SECRET" not in os.environ:
        return None
        
    return [os.getenv("ROE_KEY"), os.getenv("ROE_SECRET")]

# Post json to RoE server with proper headers and body
def post_to_roe(url, d, key, secret):
    req = urllib.request.Request(url)

    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('roe-key', key)
    req.add_header('roe-secret', secret)

    jsond = json.dumps(d)
    je = jsond.encode("utf-8")
    req.add_header('Content-Length', len(je))

    return urllib.request.urlopen(req, je)

    
def extract_roe_content(metadata_tree):
    d = {}

    try:
        # extract xpath field shorthand function
        def ext(f):
            p = metadata_tree.xpath(f)
            if (len(p) == 0):
                return ""
            elif (len(p) == 1):
                return p[0].inner_html()
            else:
                return [x.inner_html() for x in p]
        
        d = {
            "metadata": {
                "@type": "http://schema.org/Book",
                "title": ext("//dc:title"),
                "author": ", ".join((lambda c : c if type(c) is list else [c])(ext("//dc:creator"))),
                "identifier": ext("//dc:identifier"),
                "publisher": ext("//dc:publisher"),
                "language": ext("//dc:language"),
                "modified": ext("//opf:meta[@property=\"dcterms:modified\"]")
            },
            "links": [
                
            ],
            "images": []
        }
    except:
        raise se.InvalidXhtmlException
    
    return d
