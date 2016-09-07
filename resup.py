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
import argparse
import hashlib
import time
from yaml import load as yload
import re
import sys
import os
import io
import tarfile
import gzip
import shutil

#HOST = 'http://localhost:5000'
HOST = 'http://inf-vonwalha-pc.eawag.wroot.emp-eaw.ch:5000'
MAXFILESIZE = 1.5 * 2**20 # max filesize: 1.5 Mb
MAXFILESIZE = 1.5 * 2**30 # max filesize: 4Gb
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
        pa_put = subparsers.add_parser('put', help='upload ressources', parents=[papa])
        pa_put.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                            help='Name of the data package')
  
        pa_put.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='The top-level directory containing the ressources '+
                        'to be uploaded. Default is the current working directory.')


        pa_put.add_argument('--tar', action='store_true', help='create a tar archive')
        pa_put.add_argument('--gz', action='store_true', help='gzip the file(s) before upload')
        pa_put.add_argument('--keepdummy', action='store_true',
                            help='do not delete the ressource \'dummy\', if present, '+
                            'from package. The default is to delete it.')
        
        # get subcommand
        pa_get = subparsers.add_parser('get', help='download ressources', parents=[papa])
        pa_get.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                            help='Name of the data package')
  
        pa_get.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='Directory into which ressources are downloaded. ' +
                        'Default is the current working directory.')

        # list subcommand
        pa_list = subparsers.add_parser('list', help='list your packages', parents=[papa])

        
    def parse(self, arglist):
        arguments = vars(self.pa.parse_args())
        return arguments


class Put(object):
    
    def __init__(self, args):
        self.pkg_name = args['pkg_name']
        self.directory = os.path.normpath(args['directory'])
        self.gz = args['gz']
        self.tar = args['tar']
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
            'citation': '',
            'description': '',
            'name': '',
            'resource_type': 'Data_Set',
            'publication': False
        }
        metadict = dict(default_meta)
        metadict.update({'name': os.path.basename(fn)})
        return metadict

    
    def _split_file(self, filename, maxsize):
        chunksize = CHUNKSIZE
        partsdir = os.path.join(self.directory, '_parts')
        if not os.path.exists(partsdir):
            os.mkdir(partsdir)

        def newpartsfile(oldfile, count):
            if oldfile:
                oldfile.close()
            else:
                self.partfiles[filename] = []
            partsname = os.path.join(partsdir,
                                     os.path.basename(filename) +
                                     '_part_{:0=4}'.format(count))
            fpart = open(partsname, 'wb')
            print "writing new parts-file: {}".format(partsname)
            self.partfiles[filename].append(partsname)
            return(fpart)

        def update_part_metadata(filename):
            for fpart in self.partfiles[filename]:
                self.metadata[fpart] = self._mk_meta_default(fpart)
            del self.metadata[filename]

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

    def sha256(self, filename):
        hash_sha = hashlib.sha256()
        print "Calculating checksum for {} ...".format(filename)
        t0 = time.time()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_sha.update(chunk)
        digest = hash_sha.hexdigest()
        deltat = time.time() - t0
        print "time: {} seconds".format(deltat)
        print 'sha256: {}'.format(digest)
        print
        self.metadata[filename]['hash'] = digest

    def upload(self, connection):
        if self.gz:
            gzdir = os.path.join(self.directory, '_gz')
            os.mkdir(gzdir)
            print gzdir
            for f in self.metadata.keys():
                fn_out = os.path.join(gzdir, os.path.basename(f) + '.gz')
                print fn_out
                with open(f, 'rb') as fin, gzip.open(fn_out, 'wb') as fout:
                    shutil.copyfileobj(fin, fout)
                self.metadata[fn_out] = self.metadata[f]
                self.metadata[fn_out].update({'name': os.path.basename(fn_out)})
                del self.metadata[f]
            print self.metadata
                
        if self.tar:
            tfname = os.path.join(self.directory,
                                  '{}.tar'.format(os.path.basename(self.directory)))
            print 'Creating tar-archive: {}'.format(tfname)
            with tarfile.open(tfname, 'w') as tf:
                for f in self.resourcefiles:
                    tf.add(f)
                self.metadata = {tfname: self._mk_meta_default(tfname)}
                self.resourcefiles = tfname

                
        
        # Do not iterate over self.metadata - that gets changed during splitting
        # for f in self.resourcefiles:
        #     if os.stat(f).st_size > MAXFILESIZE:
        #         self._split_file(f, MAXFILESIZE)
        # for f in self.metadata.keys():
        #     self.sha256(f)
        
                
            
           
    
            
        
        
# 1048576
# update({'filename': f, 'name': f})
        
              

# def checkargs():
#     p = Parser()
#     print p.parse(sys.argv)

# #checkargs()

args = {'subcmd': 'put', 'pkg_name': 'test-the-bulk-upload',
        'keepdummy': False, 'directory': os.environ['HOME']+'/tmp/test_resup',
        'tar': False, 'gz': True}
# pa = Parser()
# args = pa.parse(sys.argv)
print "Arguments = {}".format(args)
c = Connection(args)
if args['subcmd'] == 'put':
    put = Put(args)
    put.upload(c)


# put = Put(args)


# if __name__ == '__main__':
#     pass
    



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

