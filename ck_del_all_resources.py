import ckanapi
import os
import pprint

HOST = 'http://inf-vonwalha-pc.eawag.wroot.emp-eaw.ch:5000'
APIKEY = os.environ['CKAN_APIKEY']

pkgname = 'test-the-bulk-upload'
delres = 'all'

c = ckanapi.RemoteCKAN(HOST, APIKEY)

def del_resources(c, pkgname, delres):
    pkg = c.call_action('package_show', {'id': pkgname})
    resources = [(res['name'], res['id']) for res in pkg['resources']]
    delids = [r[1] for r in resources if (r[0] in delres) or (delres == 'all')]
    for rid in delids:
        c.call_action('resource_delete', {'id': rid})

def show_resources(c, pkgname):
    pkg = c.call_action('package_show', {'id': pkgname})
    resources = [(res['name'], res['id']) for res in pkg['resources']]
    pprint.pprint(resources)

    
#del_resources(c, pkgname, 'all')
show_resources(c, pkgname)

#res = c.call_action('resource_show', {'id': 'a0f89382-0442-446c-9127-3a3f4371da94'})

# test download & concatenate
ids = ['fdca2fe8-884d-43f8-937c-6bf4539a867b' , 'cb2307c2-2550-4506-be52-06333ab3c42d']
destfile = '/home/vonwalha/tmp/test_resup/get/testget100'

