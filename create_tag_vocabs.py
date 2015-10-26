import requests
import os
import re
import json
import ckanapi

host = "http://localhost:5000"
apikey = os.environ['CKAN_APIKEY_HVW_ADM']
systemsdef = os.path.join(os.environ['HOME'], "Ckan/static/systems_def.txt")
ckan = ckanapi.RemoteCKAN(host, apikey=apikey)

vocab_name = "systems"

with open(systemsdef) as f:
    tags = [x.strip('\n') for x in f.readlines()]

tagdict = [dict([('vocabulary_id', vocab_name), ('name', t)]) for t in tags]

vocab = ckan.call_action('vocabulary_create', {'name': vocab_name})

for t in tagdict:
    ckan.call_action('tag_create', {'name': t['name'], 'vocabulary_id': vocab['id']})

    

## consider display names
## add to schema
## add to templates
