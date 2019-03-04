import sys
import os
import xml.etree.ElementTree as ET 
import urllib.request
import json
from dotenv import load_dotenv

REQUIRED_FIELDS = {
    "title": "title",
    "author": "creator",
    "isbn": "",
    "version": "meta;se:revision-number"
}
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

# parse content.opf and retrieve relevant data
def parse_content(contentfile):
    if not os.path.exists(contentfile):
        print("Invalid ePUB directory")
        return None
    
    data = {}
    try:
        #parse content xml and get metadata
        xml = ET.parse(contentfile)
        root = xml.getroot()
        metadata = [x for x in root if x.tag[-8:] == "metadata"][0]
        
        #iterate through metadata and extract relevant fields by tag
        #if field has semicolon, match tag and also property (there are many meta tags but they have different property attributes)
        for child in metadata:
            for key, value in REQUIRED_FIELDS.items():
                spl = value.split(";")
                tag = spl[0]

                if tag == child.tag[-len(tag):]:
                    if len(spl) == 1:
                        data[key] = child.text
                        break
                    else:
                        if not "property" in child.attrib or child.attrib["property"] != spl[1]:
                            continue

                        data[key] = child.text

        #remove url prefix from source attribute
        if "source" in data and data["source"][:4] == "url:":
            data["source"] = data["source"][4:]
    except:
        print(e)
        return None

    return data



def main():
    if len(sys.argv) != 2:
        print("Wrong number of arguments. Usage: python3 roe-upload.py <path-to-directory>")
        return
    
    path = sys.argv[1]

    if not os.path.isdir(path):
        print("ePUB directory invalid")
        return

    contentfile = "{}/src/epub/content.opf".format(path)
    content = parse_content(contentfile)

    if content is None:
        print("Error parsing content file. Ensure /src/epub/content.opf exists in the directory, is formatted properly, and has the necessary data.")
        return
    
    credentials = get_credentials()

    if credentials is None:
        print("Credentials not found. Set environment variables ROE_KEY and ROE_SECRET.")
        return

    response = post_to_roe(POST_URL, content, credentials[0], credentials[1])
    print(response)

if __name__ == "__main__":
    main()