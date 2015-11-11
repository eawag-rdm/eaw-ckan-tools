import requests
import os
import re
import json
import ckanapi

#host = "http://localhost:5000"
host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
pic_dict = os.path.join(os.environ['HOME'], "Ckan/static/orga_pics")
apikey = os.environ['CKAN_APIKEY_HVW_ADM']

ckan = ckanapi.RemoteCKAN(host, apikey=apikey)
organizations = ckan.action.organization_list()

def match_orga2pics(pdict, olist):
    upd = []
    for o in organizations:
        for p in os.listdir(pic_dict):
            if os.path.splitext(p)[0] == o:
                upd.append({'id': o, 'pic': os.path.join(pic_dict, p)})
    return(upd)

upd = match_orga2pics(pic_dict, organizations)

for org in upd:
    print("updating {} with {}".format(org['id'], org['pic']))
    with open(org['pic']) as f:
        ckan.action.organization_update(id=org['id'], image_upload=f)
