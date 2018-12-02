
from google.cloud import storage
import hmac
from hashlib import sha1
import requests
import subprocess
import zipfile
import os

def hello_world(request):
    secret = bytes(os.environ.get("secret"),encoding='utf=8')
    #verify header sig using sha
    header_signature = request.headers.get('X-Hub-Signature').replace('sha1=','')
    header = request.headers
    data = request.data
    payload = request.get_json()
    mac = hmac.new(secret, msg=data, digestmod=sha1)
    if str(mac.hexdigest()) == str(header_signature):
        bucket_name = 'www.hardscrabblelabs.com'
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)

        url = "https://github.com/ajtrexler/gcp_landing/archive/master.zip"
        github_handle = requests.get(url)
        tmp_raw = github_handle.content

        with open('/tmp/tmpzip.zip','wb') as fid:
            fid.write(tmp_raw)
        
        zipfile.ZipFile('/tmp/tmpzip.zip','r').extractall('/tmp')
        rootdir = '/tmp/gcp_landing-master/_site/'
        for folder,subs,files in os.walk(rootdir):
            for f in files:
                blob = bucket.blob(os.path.join(folder.replace(rootdir,'')+f))
                blob.upload_from_filename(os.path.join(folder,f))

        return 'blob up success'

    else:
        return "{x} : {y}".format(x=mac.hexdigest(),y=header_signature)

