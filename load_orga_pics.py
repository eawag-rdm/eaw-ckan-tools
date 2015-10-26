import requests
import os
import re
import json
import ckanapi

host = "http://localhost:5000"
apipath = host + "/api/3/action/"
pic_dict = os.path.join(os.environ['HOME'], "Ckan/static/orga_pics")

ckan = ckanapi.RemoteCKAN(host, apikey=apikey)
organizations = ckan.action.organization_list()


#################################################
# TEST: new organization
pic_url = os.path.join(pic_dict, 'Ecoimpact.jpg')

ckan.action.organization_update(id='ecoimpact2', image_upload=open(pic_url))



res = requests.post(url, json=datajson, headers=header, files=file)

def match_orga2pics(pdict, olist):
    upd = []
    for o in organizations:
        for p in os.listdir(pic_dict):
            if os.path.splitext(p)[0] == o:
                upd.append({'id': o, 'pic': os.path.join(pic_dict, p)})
    return(upd)


organizations = requests.get(apipath+"organization_list").json()['result']

upd = match_orga2pics(pic_dict, organizations)

res = requests.post(apipath + 'organization_update',
                    json = json.dumps({'name': 'testapi'}),
                    headers=auth)



print(res)
print(res.reason)
                             
# def get_all_ds_res(host):
#     r = requests.get(host+restpath+"current_package_list_with_resources")
#     return(r.json())

# def get_all_ds(host):
#         r = requests.get(host+restpath+"package_list")
#         return(r.json())

res = requests.post(apipath + 'organization__create',
                   
                   data={'name':'testapi'})

url = "http://localhost:5000/api/3/action/organization_create"
datajson = {"name": "testapi3"}
file = {"image_upload": open('/home/vonwalha/Ckan/static/orga_pics/aquatic-ecology.jpg')}
header = {"Authorization": "298b9601-6693-4fc8-96ac-fc500e61b82f"}
res = requests.post(url, json=datajson, headers=header, files=file)
print(res)


CHECK OUT CKANAPI

WE NEED ALL DATA AS UTF8-string
