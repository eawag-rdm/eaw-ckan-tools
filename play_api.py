import requests

localhost = "http://localhost:5000"
remotehost = "http://eaw-test-ckan.eawag.wroot.emp-eaw.ch"
restpath = "/api/3/action/"

def get_all_ds_res(host):
    r = requests.get(host+restpath+"current_package_list_with_resources")
    return(r.json())

def get_all_ds(host):
        r = requests.get(host+restpath+"package_list")
        return(r.json())

