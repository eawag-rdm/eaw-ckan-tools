#!/usr/bin/env python
## Specification ###############################################################
#
# Input:
# package-name
# Directory

# Options:
#    -tar tar the directory-tree into one archive-file
#         if not given, upload each file individually

#    -gz  gzip each individual file first, in case it is not yet compressed
#
#    -get downloads ressources and assembles them if necessary
#
#
#
# Meta Data:
# Default: name = filename
# Notes, description = ''
# The publication = 'no'
# Resource Type = 'Compound' (tar) or 'Data_Set' (indiv. files)
#
# Functionality:
# Override default metadata
# Warn if a ressource is being replaced
# Split file(s) if file is too large ( > 4GB ) in smaller chunks for upload.
# Calculate hash digest
# Remove ressource named "dummy"
#
# Read a definition-file in the given directory to:
#    + select files using a regex
#    + assign meta-data based on regex selection for individual fields
# 
#
# CKAN TODO: Add ressource type: Compound (for tar archives with multiple types)
#            Add meta-data to indicate a split ressource.
#            Display file size in web-UI
#
#
# Extra functions:
# + list my packages
# + simple search in my packages
#
#
### "Override Metadata" functionality:   #######################################
#
# provide a file in the (top level) directory
# YAML - format
# selector as regex (applied to filenames)
# overwrite datum: value
#
# For tar-archive: no selector accepted
################################################################################

import ckanapi
import requests
import argparse
import hashlib
import tarfile
import time
import gzip
import shutil
import uuid
#from yaml import load as yload
from pprint import pprint
import re
import sys
import os
import io


#HOST = 'http://localhost:5000'
HOST = 'http://inf-vonwalha-pc.eawag.wroot.emp-eaw.ch:5000'
MAXFILESIZE = 10 * 2**20 # max filesize: 10Mb
#MAXFILESIZE = 4 * 2**30 # max filesize: 4Gb
CHUNKSIZE = 4 * 2**10   # for tuning

class Connection(object):
    def __init__(self, args):
        try:
            apikey = args.get('k') or [os.environ['CKAN_APIKEY']]
        except KeyError:
            print 'ERROR: No API key found. Either provide it with with the \'-k\' ' +\
                'option or set the environment variable \'CKAN_APIKEY\', e.g. ' +\
                'in bash:\n\'export CKAN_APIKEY=xxxxxxxxxxxxxxxxxxxxx\''
            sys.exit(1)
        else:
            apikey = apikey[0]
        server = args.get('s') or [HOST]
        server = server[0]
        self.conn = ckanapi.RemoteCKAN(server, apikey=apikey)

    def get_connection(self):
        return self.conn
    
class Parser(object):
    def __init__(self):
        self.pa = argparse.ArgumentParser(description='Batch upload of ressources '+
                        'to a data package in CKAN',
                        epilog=os.path.basename(sys.argv[0]) +
                        ' {put | get | list} -h for specific help on subcommands.')

        # parent parser (common arguments for all subcommands)
        papa = argparse.ArgumentParser(add_help=False)
        papa.add_argument('-s', type=str, metavar='SERVER', nargs=1,
                          help='CKAN server (default is '+HOST+')')
                          
        papa.add_argument('-k', nargs=1, metavar='API_KEY',
                          help='Your API-key. If omitted, the environment variable \'CKAN_APIKEY\' will be used.')

      
        subparsers = self.pa.add_subparsers(help='subcommands', dest='subcmd')
        
        # put subcommand
        pa_put = subparsers.add_parser('put', help='upload ressources',
                                       parents=[papa],
                                       description='Upload a batch of files ' +
                                       'as resources to CKAN.')
        pa_put.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                            help='Name of the data package')
  
        pa_put.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                            default=os.curdir,
                            help='The directory containing the ressources '+
                            'to be uploaded. Default is the current working ' +
                            'directory. Subdirectories are ignored.')


        pa_put.add_argument('--tar', action='store_true', help='create a tar archive')
        pa_put.add_argument('--gz', action='store_true', help='gzip the file(s) before upload')
        pa_put.add_argument('--keepdummy', action='store_true',
                            help='do not delete the ressource \'dummy\', if present, '+
                            'from package. The default is to delete it.')
        
        # get subcommand
        pa_get = subparsers.add_parser('get', help='download ressources',
                                       parents=[papa],
                                       description='Bulk download '+
                                       'resources of a package in CKAN.')
        pa_get.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                            help='Name of the data package')
  
        pa_get.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='Directory into which ressources are downloaded. ' +
                        'Default is the current working directory.')
        
        pa_get.add_argument('resources', metavar='RESOURCES', type=str, nargs='?',
                        default='.*',
                        help='The name of the resource to be downloaded or ' +
                        'a regular expression that matches the resources ' +
                        'to be downloaded, e.g. \".*\" (the default!)')
   

        # list subcommand
        pa_list = subparsers.add_parser('list', help='list your packages',
                                        parents=[papa],
                                        description='List the packages that '+
                                        'you can modify.')

        # delete subcommand
        pa_del = subparsers.add_parser('del', help='delete resources',
                                       parents=[papa],
                                       description='Batch delete resoures of '+
                                       'a package in CKAN.')
        
        pa_del.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                            help='Name of the data package')
        
        pa_del.add_argument('resources', metavar='RESOURCES', type=str, nargs='?',
                            default='.*',
                            help='The name of the resource to be deleted or ' +
                            'a regular expression that matches the resources ' +
                            'to be deleted, e.g. \".*\" (the default!)')
        
    def parse(self, arglist):
        arguments = vars(self.pa.parse_args())
        return arguments


class Put(object):
    
    def __init__(self, args):
        self.pkg_name = args['pkg_name']
        self.directory = os.path.normpath(args['directory'])
        self.connection = args['connection']
        self.gz = args['gz']
        self.tar = args['tar']
        self.keepdummy = args['keepdummy']
        allfiles = [os.path.normpath(os.path.join(self.directory, f))
                    for f in os.listdir(self.directory)
                    if os.path.isfile(os.path.normpath(
                            os.path.join(self.directory, f)))]
        self.resourcefiles = [f for f in allfiles
                              if not re.match('.*\.(yaml|yml)', f)]
        self.metafiles = [f for f in allfiles
                              if re.match('.*\.(yaml|yml)', f)]
        self.metadata = {f: self._mk_meta_default(f) for f in self.resourcefiles}
        self.partfiles = {}

    def _mk_meta_default(self, fn):
        default_meta = {
            'package_id': self.pkg_name,
            'citation': '',
            'description': '',
            'name': '',
            'resource_type': 'Data_Set',
            'publication': False,
            'url': ''
        }
        metadict = dict(default_meta)
        metadict.update({'name': os.path.basename(fn)})
        return metadict

    
    def _split_files(self):

        def newpartsfile(oldfile, count):
            if oldfile:
                oldfile.close()
            else:
                self.partfiles[filename] = []
            partsname = os.path.join(partsdir,
                                     os.path.basename(filename) +
                                     '_part_{:0=4}'.format(count))
            fpart = open(partsname, 'wb')
            print "    writing new parts-file: {}".format(partsname)
            self.partfiles[filename].append(partsname)
            return(fpart)

        def update_part_metadata(filename):
            for fpart in self.partfiles[filename]:
                self.metadata[fpart] = dict(self.metadata[filename])
                self.metadata[fpart]['name'] = os.path.basename(fpart)
            del self.metadata[filename]

        maxsize = MAXFILESIZE
        chunksize = CHUNKSIZE
        partsdir = os.path.join(self.directory, '_parts')
        if not os.path.exists(partsdir):
            os.mkdir(partsdir)
        
        for filename in [f for f in self.metadata.keys()
                         if os.stat(f).st_size > maxsize]:
            print "splitting {}".format(filename)
            cur_partsfile = newpartsfile(None, 0)
            cur_size = 0
            count = 0
            with open(filename, 'rb') as f:
                for chunk in iter(lambda: f.read(chunksize), b''):
                    cur_size += chunksize
                    if cur_size > maxsize:
                        count += 1
                        cur_partsfile = newpartsfile(cur_partsfile, count)
                        cur_size = chunksize
                    cur_partsfile.write(chunk)
                cur_partsfile.close()
            update_part_metadata(filename)

    def _sha256(self):
        for filename in self.metadata.keys():
            hash_sha = hashlib.sha256()
            print "Calculating checksum for {} ...".format(filename)
            t0 = time.time()
            with open(filename, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_sha.update(chunk)
            digest = hash_sha.hexdigest()
            deltat = time.time() - t0
            print "    time: {} seconds".format(deltat)
            print '    sha256: {}'.format(digest)
            self.metadata[filename]['hash'] = digest

    def _gnuzip(self):
        gzdir = os.path.join(self.directory, '_gz')
        if not os.path.exists(gzdir):
            os.mkdir(gzdir)
        for f in self.metadata.keys():
            fn_out = os.path.join(gzdir, os.path.basename(f) + '.gz')
            print 'compressing {} ...'.format(f)
            with open(f, 'rb') as fin, gzip.open(fn_out, 'wb') as fout:
                shutil.copyfileobj(fin, fout)
            self.metadata[fn_out] = self.metadata[f]
            self.metadata[fn_out].update({'name': os.path.basename(fn_out)})
            del self.metadata[f]

    def _tar(self):
        tardir = os.path.join(self.directory, '_tar')
        if not os.path.exists(tardir):
            os.mkdir(tardir)
        fn_out = os.path.join(tardir,
                              os.path.basename(self.directory) +'.tar')
        print 'Creating tar-archive: {}'.format(fn_out)
        with tarfile.open(fn_out, 'w') as tf:
            for f_in in self.metadata.keys():
                print '    adding file {}'.format(f_in)
                tf.add(f_in)
        self.metadata = {fn_out: self._mk_meta_default(fn_out)}

    def _upload(self):
        for res in sorted(self.metadata.keys()):
            self.metadata[res]['size'] = os.stat(res).st_size
            print "uploading {} ({})".format(res, self.metadata[res]['size'])
            self.connection.call_action('resource_create', self.metadata[res],
                                files={'upload': open(res, 'rb')})

    def upload(self):
        if self.gz:
            self._gnuzip()    
        if self.tar:
            self._tar()
        self._split_files()
        self._sha256()
        self._upload()
        if not self.keepdummy:
            del_resources({'pkg_name': self.pkg_name,
                           'connection': self.connection,
                           'resources': 'dummy'})

                 
class Get(object):
    def __init__(self, args):
        self.conn = args['connection']
        self.pkg_name = args['pkg_name']
        self.directory = os.path.normpath(args['directory'])
        self.resources = args['resources']
        self.partpatt = re.compile('^(?P<basename>.+)_part_(?P<idx>\d+)$')
        self.downloaddict = {}
        check_package(args)
        self._checkdir()
        try:
            self.resources = re.compile(self.resources)
        except:
            print('It seems "{}" is not a valid regular expression.'
                  .format(self.resources))
            print('Aborting!')
            sys.exit(1)


    def _checkdir(self):
        testfile =  os.path.join(self.directory,
                                 'testwriteable_64747354612458526831012')
        try:
            with open(testfile, 'wb') as test:
                test.write('0')
        except:
            sys.exit('Can\'t write in {}. Aborting.'.format(self.directory))
        else:
            os.remove(testfile)

    def _getresources(self):
        res = self.conn.call_action('package_show', {'id': self.pkg_name})
        res = res.get('resources')
        if not res:
            print 'No resources in package {}. Aborting.'.format(self.pkg_name)
            sys.exit(1)
        return(res)

    def _downloaddict(self, res):

        for r in res:
            resnew = {'url': r['url'], 'id': r['id'],
                      'hash': r['hash'], 'idx': 0}
            match = re.match(self.partpatt, r['name'])
            if match:
                basnam, idx = match.group(1, 2)
                idx = int(idx)
                resnew.update({'idx': idx})
                if basnam in self.downloaddict:
                    self.downloaddict[basnam].append(resnew)
                else:
                    self.downloaddict[basnam] = [resnew]
            else:
                if r['name'] in self.downloaddict:
                    r['name'] += str(uuid.uuid4())
                self.downloaddict[r['name']] = [resnew]
                
        for k in self.downloaddict.keys():
            v = sorted(self.downloaddict[k],
                       lambda x,y: x-y, lambda x: x.get('idx'))
            self.downloaddict[k] = v

    def _download(self):
        for f_out_base in self.downloaddict.keys():
            f_out = os.path.join(self.directory, f_out_base)
            
            if os.path.exists(f_out):
                answer = raw_input('File {} exists. Overwrite? [Y/N] '
                                   .format(file_out_base))
                if answer not in ['y', 'Y', 'yes', 'Yes', 'YES']:
                    sys.exit('aborted.')
                else:
                    os.remove(file_out)
##############################   FIX FROM HERE #################################            
            with io.open(f_out, mode='ab') as fout:
                for partslist in self.downloaddict[f_out_base]:
                    for part in partslist:
                        r = requests.get(part['url'])
                        instream = io.BytesIO(r.content)
                        chunk = True
                        sha = hashlib.sha256()
                        while chunk:
                            chunk = instream.read1(CHUNKSIZE)
                            sha.update(chunk)
                            fout.write(chunk)
                        print "digest for {}:".format(url)
                        print sha.hexdigest()

    
    def get(self):
        print vars(self)
        res = self._getresources()
        print "Pattern: {}".format(self.resources)
        res = [r for r in res if re.match(self.resources, r['name'])]
        self._downloaddict(res)
        self._download()
        


# if os.path.exists(file_out):
#     answer = raw_input('File {} exists. Overwrite? [Y/N] '.format(file_out_base))
#     if answer not in ['y', 'Y', 'yes', 'Yes', 'YES']:
#         sys.exit('aborted.')
#     else:
#         os.remove(file_out)
# with io.open(file_out, mode='ab') as fout:
#     for url in files:
#         r = requests.get(url)
#         instream = io.BytesIO(r.content)
#         chunk = True
#         sha = hashlib.sha256()
#         while chunk:
#             chunk = instream.read1(CHUNKSIZE)
#             sha.update(chunk)
#             fout.write(chunk)
#         print "digest for {}:".format(url)
#         print sha.hexdigest()

        #print self.__dict__
        # check if directory writeable
        # get ids and names of all resources
        # collect into basefilename -> list of ids
          # consider (rename) duplicate resource names
        # download & concatenate

def del_resources(args):
    pkg_name = args['pkg_name']
    conn = args['connection']
    resources = args['resources']
    try:
        resources = re.compile(resources)
    except:
        print('It seems "{}" is not a valid regular expression.'
              .format(resources))
        print('Aborting!')
        sys.exit(1)
    check_package(args)
    pkg = conn.call_action('package_show', {'id': pkg_name})
    allres = [(res['name'], res['id']) for res in pkg['resources']]
    delres = [(r[0], r[1]) for r in allres if re.match(resources, r[0])]
    for r in delres:
        print "DELETING Resources: {}".format(r[0])
        c.call_action('resource_delete', {'id': r[1]})

def check_package(args):
    conn = args['connection']
    pkgname = args['pkg_name']
    pkgs = conn.call_action('package_list')
    if pkgname not in pkgs:
        sys.exit('No package "{}" found. Aborting.'.format(pkgname))


def list_packages(args):
    conn = args['connection']
    orgas = conn.call_action('organization_list_for_user',
                             {'permission': 'update_dataset'})
    oids = [o['id'] for o in orgas]
    searchquery = '('+' OR '.join(['owner_org:{}'.format(oid) for oid in oids]) + ')'
    res = conn.call_action('package_search', {'q': searchquery,
                                              'include_drafts': True,
                                              'rows': 1000,
                                              'include_private': True})['results']
    pkgs = [p['name'] for p in res]
    for p in pkgs:
        print p
    


args = {'subcmd': 'get', 'pkg_name': 'test-the-bulk-upload',
        'resources': '.*',
        'keepdummy': False, 'directory': os.environ['HOME']+'/tmp/test_resup/get',
        'tar': True, 'gz': True}

if __name__ == '__main__':
    pa = Parser()
    args = pa.parse(sys.argv)


c = Connection(args).get_connection()
args.update({'connection': c})
print "Arguments = {}".format(args)

if args['subcmd'] == 'put':
    put = Put(args)
    put.upload()
if args['subcmd'] == 'get':
    get = Get(args)
    #get.get()
if args['subcmd'] == 'del':
    del_resources(args)
if args['subcmd'] == 'list':
    list_packages(args)
    


    


# with open('/home/vonwalha/tmp/test_resup/metadata.yaml', 'r') as f:
#     test = yload(f)

# def split_file(filename, maxsize):
#     partsdir = '/home/vonwalha/tmp/test_resup/parts'
#     chunksize = 4 * 1024
#     if not os.path.exists(partsdir):
#         os.mkdir(partsdir)
#     count = 0

#     def newpartsfile(oldfile, count):
#         if oldfile:
#             oldfile.close()
#         partsname = os.path.join(partsdir,
#                                  os.path.basename(filename) +
#                                  '_part_{:0=4}'.format(count))
#         fpart = open(partsname, 'wb')
#         print "partsname is {}".format(partsname)
#         return(fpart)

#     cur_partsfile = newpartsfile(None, 0)
#     cur_size = 0
#     count = 0
#     with open(filename, 'rb') as f:
#         for chunk in iter(lambda: f.read(chunksize), b''):
#             cur_size += chunksize
#             if cur_size > maxsize:
#                 count += 1
#                 cur_partsfile = newpartsfile(cur_partsfile, count)
#                 cur_size = chunksize
#             cur_partsfile.write(chunk)

# filename = '/home/vonwalha/tmp/test_resup/5000M.test'
# maxsize = 2 * 2**30
# for chunksize in [1024, 2048, 4*1024, 8*1024, 1024*1024]:
#     t0 = time.time()
#     split_file(filename, maxsize, chunksize)
#     print "chunksize: {} -- time: {}".format(chunksize, time.time()-t0)

