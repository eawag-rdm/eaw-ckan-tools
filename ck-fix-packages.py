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
    def fixpackage_newfields(self, idn):
        newpkg = copy.deepcopy(pm.pkg(idn))
        for f in self.newfields.keys():
            if f not in newpkg:
                print "setting {} to {}".format(f, newfields[f])
                newpkg[f] = newfields[f]
        return(newpkg)

    def checkpkg_reupload(self, idn, respack):
        try:
            respack.append(self.action('package_update', self.pkg(idn)))
        except ckanapi.errors.ValidationError as e:
            return False
        else:
            return True

    def fixpackage_Image2Bitmap_Image(self, idn):
        newpkg = copy.deepcopy(pm.pkg(idn))
        resources = newpkg.get('resources', [])
        changed = False
        restypes = [(i, x.get('resource_type')) for i, x in enumerate(resources)]
        for i, t in restypes:
            if t == 'Image':
                changed = True
                newpkg['resources'][i]['resource_type'] = 'Bitmap Image'
                print "replacement in {}".format(newpkg['name'])
        if changed:
            return(newpkg)
        else:
            return(False)

    def fixpackage_rename_field(self, idn, oldname, newname):
        newpkg = copy.deepcopy(pm.pkg(idn))
        if newpkg.get(oldname, {}):
            print ("Found {} in {}, renaming to {}"
                   .format(oldname, idn, newname))
            newpkg[newname] = newpkg[oldname]
            del newpkg[oldname]
            return newpkg
        else:
            return False
        
    def fixpackage_patch_missing(self, idn, fields):
        newpkg = copy.deepcopy(pm.pkg(idn))
        changed = False
        for f in fields:
            if not newpkg.get(f['name'], {}) or f['force']:
                changed = True
                print ("setting {} in {} to {}"
                       .format(f['name'], idn, f['default']))
                newpkg[f['name']] = f['default']
        if changed:
            return newpkg
        else:
            return False

    def fixpackage_timerange_quotes(self, idn):
        newpkg = copy.deepcopy(pm.pkg(idn))
        timerangelist = newpkg.get('timerange')
        changed = False
        if not isinstance(timerangelist, list):
            print("Problem: {} ({}) in {} not a list"
                  .format(timerangelist, type(timerangelist),newpkg.get('name')))
            return
        for i,s in enumerate(timerangelist):
            if not isinstance(s, basestring):
                print("Problem: {} ({}) in {} not a string"
                .format(s, type(s),newpkg.get('name')))
                return
            if s.find("TO") != -1 and (s[0] != '[' and s[-1] != ']'):
                print "Need for replacement: {} in {}".format(
                    s, newpkg.get('name'))
                changed = True
                timerangelist[i] = '[' + s + ']'
                print "Repaced: {}".format(newpkg.get('timerange'))
        if changed:
            return newpkg
        else:
            return False

    def fixpackage_extras_species2taxa(self, idn, newpkg=False):
        newpkg = copy.deepcopy(pm.pkg(idn)) if not newpkg else newpkg
        extras = newpkg.get('extras')
        taxa = newpkg.get('taxa', None)
        changed = False
        if extras:
            ekeys = [x['key'] for x in extras]
            for i, k in enumerate(ekeys):
                if k == 'species':
                    changed = True
                    del extras[i]
        if taxa is None:
            newpkg['taxa'] = ''
        if changed:
            return newpkg
        else:
            return False
            
        
        

# ###############################################


#pm = PackageModifier(host, apikey)
pm = PackageModifier(localhost, apikey)


# Assume that "fixpackage_whatever returns the replacement package
# if need be fixed, else False

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
    newpkg = pm.fixpackage_timerange_quotes(idn)
    #newpkg = pm.fixpackage_Image2Bitmap_Image(idn)
    #newpkg = pm.fixpackage_extras_species2taxa(idn)
    # newpkg = pm.fixpackage_patch_missing(idn, [{'name': 'systems',
    #                                             'default': 'none',
    #                                             'force': False}])
    # newpkg = pm.fixpackage_extras_species2taxa(idn, newpkg)
    if newpkg:
        print "Package Update: {}".format(newpkg['name'])
        respack.append(pm.action('package_update', newpkg))

## Individual ckecks
# idn = 'light-microscopy-for-sgier2016'
# p = [x for x in respack if x['name'] == idn][0]
# ckan = ckanapi.RemoteCKAN(host, apikey=apikey)
# ckan.call_action('package_update', p)

 
# tr = [(v['name'], v['timerange'], type(v['timerange'])) for k,v in pm.packages.iteritems()]
# #tr = [(v['name'], v.get('substances')) for k,v in pm.packages.iteritems()]
# trt = [x[1] for x in tr]



    
