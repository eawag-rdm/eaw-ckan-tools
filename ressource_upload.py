import ckanapi
import os
import hashlib
import magic


import time

BUFSIZE = 2**16
host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
apikey = os.environ['CKAN_APIKEY']

ckan = ckanapi.RemoteCKAN(host, apikey=apikey)
SOURCEDIR = '/home/vonwalha/rdm/data/fishec/pilotdataset/whitefish_fasta'
PACKAGE_ID = 'whitefish-genomics'
RESOURCE_TYPE = 'Data_Set'


def list_of_files(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def upload1(f, package_id, resource_type, hashdigest, mimetype):
    data_dict = {
        'package_id': package_id,
        'url': 'dummy',
        'name': os.path.basename(f),
        'resource_type': resource_type,
        'hash': hashdigest,
        'mimetype': mimetype
    }
    ckan.call_action('resource_create', data_dict,
                     files={'upload': open(list_of_files(SOURCEDIR)[0], 'rb')})

def filehash(f, algo):
    exec('hasher = hashlib.' + algo + '()')
    with open(f, 'rb') as fi:
        buf = fi.read(BUFSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fi.read(BUFSIZE)
    return hasher.hexdigest()

def mimetype(f):
    return magic.from_file(f, mime=True)


def main():
    for f in list_of_files(SOURCEDIR):
        print f
        print "Calculating hash for {} ...".format(os.path.basename(f))
        print f
        hashdigest = filehash(f, 'sha256')
        print "Mimetype of {}:".format(os.path.basename(f))
        mime=mimetype(f)
        print(mime)
        print "Uplaoding file {}".format(os.path.basename(f))
        res = upload1(f, PACKAGE_ID, RESOURCE_TYPE, hashdigest, mime)
        print "Result:"
        print(res)

main()
 
