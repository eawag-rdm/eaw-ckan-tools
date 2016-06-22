###############################################################
#
# A class to systematically modify packages
# HvW -2016-06-22
#
###############################################################

import os
import argparse
from pprint import PrettyPrinter
import ckanapi
import json
import copy

pp = PrettyPrinter(indent = 2)

apikey = os.environ['CKAN_APIKEY']
host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
localhost = "http://localhost:5000"


class PackageModifier(object):
    def __init__(self, host, apikey):
        self.ckan = ckanapi.RemoteCKAN(host, apikey=apikey)
        self.action = self.ckan.call_action
        self.packagelist = self.action('package_list')
        self.packages = {}
        self.subpkgs = {}
        self.failed_pkgs = []
        self.newfields = {'systems': 'none',
                          'generic-terms': 'none',
                          'variables': 'none',
                          'species': [],
                          'substances': [],}


    def print_pkglist(self):
        pp.pprint(self.packagelist)

    def mk_subpkgs(self, fieldname):
        self.subpkgs = [{'id': key[0], fieldname: val[fieldname]}
                            for key, val in self.packages.iteritems()]

    def pkg(self, idn):
        for k in self.packages.keys():
            if idn in k:
                return(self.packages[k])
        return(None)
    
    def dl_pkg(self, pkg_name):
        if pkg_name == '_all':
            pkg_name = self.packagelist
            self.failed_pkgs = []
        else:
            pkg_name = [pkg_name]
        for pn in pkg_name:
            print "Downloading meta-data for {}".format(pn)
            try:
                pkg  = self.action('package_show', {'id': pn})
            except ckanapi.errors.CKANAPIError:
                self.failed_pkgs.append(pn)
                print "Failed to download package {}".format(pn)
            else:
                self.packages[(pkg['id'], pkg['name'])] = pkg
        print "Success: {} , Failure: {}".format(len(self.packages),
                                                 len(self.failed_pkgs))

    def mk_patchdicts(self, fieldname, func):
        self.patchdicts = copy.deepcopy(self.subpkgs)
        [p.update({fieldname: func(p[fieldname])})
         for p in self.patchdicts]


    def trafo_timerange(self, v):
        return(json.dumps(v))

    def patch(self, feedback=False):
        patchdicts = self.subpkgs if feedback else self.patchdicts 
        for data_dict in patchdicts:
            pkgname = self.pkg(data_dict['id'])['name']
            print "Patching {}".format(pkgname)
            self.action('package_patch', data_dict)
            
    def id2name(self, idn):
        return self.pkg(idn)['name']

    def name2id(self, name):
        return self.pkg(name)['id']
    
    def clear_packages(self):
        self.packages = {}

    def info(self, idn):
        id = self.pkg(idn)['id']
        name = self.pkg(idn)['name']
        print "id: {} name: {}".format(idn, name)
        print "timerange: {}".format(self.pkg(idn)['timerange'])

    # set new required fields (self.newfields) to default values
    def fixpackage(self, idn):
        newpkg = copy.deepcopy(pm.pkg(idn))
        for f in self.newfields.keys():
            if f not in newpkg:
                print "setting {} to {}".format(f, newfields[f])
                newpkg[f] = newfields[f]
        return(newpkg)

# ###############################################


pm = PackageModifier(host, apikey)
#pm = PackageModifier(localhost, apikey)

# Get package, try updating with package gotten.
# Record packages that can't be downloaded.
# Fix packages with which the re-update failed,
#  (here, add new fields with default values)
respack = []
for idn in pm.packagelist:
    print "Checking package {}".format(idn)
    pm.dl_pkg(idn)
    if idn in pm.failed_pkgs:
        continue
    pm.info(idn)
    try:
        respack.append(pm.action('package_update', pm.pkg(idn)))
    except ckanapi.errors.ValidationError as e:
        newpkg = pm.fixpackage(idn)
        respack.append(pm.action('package_update', newpkg))
