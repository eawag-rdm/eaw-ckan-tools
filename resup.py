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
from yaml import load as yload
import re
import sys
import os
import io


class Parser(object):
    def __init__(self):
        self.pa = argparse.ArgumentParser(description='Batch upload of ressources '+
                        'to a data package in CKAN',
                        epilog=os.path.basename(sys.argv[0]) +
                        ' {put | get | list} -h for specific help on subcommands.')
        
        subparsers = self.pa.add_subparsers(help='subcommands', dest='subcmd')
        # put subcommand
        pa_put = subparsers.add_parser('put', help='upload ressources')
        
        pa_put.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                        help='Name of the data package')
        pa_put.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='The top-level directory containing the ressources '+
                        'to be uploaded. Default is the current working directory.')
        pa_put.add_argument('-tar', action='store_true', help='create a tar archive')
        pa_put.add_argument('-gz', action='store_true', help='gzip the file(s) before upload')
        pa_put.add_argument('-keepdummy', action='store_true',
                            help='do not delete the ressource \'dummy\', if present, '+
                            'from package. The default is to delete it.')
        
        # get subcommand
        pa_get = subparsers.add_parser('get', help='download ressources')
        pa_get.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                        help='Name of the data package')
        pa_get.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='Directory into which ressources are downloaded. ' +
                        'Default is the current working directory.')
        # list subcommand
        pa_list = subparsers.add_parser('list', help='list your packages')
        
    def parse(self, arglist):
        arguments = vars(self.pa.parse_args())
        return arguments


class Put(object):
    
    def __init__(self, args):
        self.pkg_name = args['pkg_name']
        self.directory = args['directory']
        self.gz = args['gz']
        self.tar = args['tar']
        self.allfiles = os.listdir(self.directory)
        self.exceptfiles = [f for f in self.allfiles
                            if not re.match('.*\.(yaml|yml)', f)]
        self.metadata = self._assign_metadata()
        print self.metadata
        
    def _assign_metadata(self):
        default_meta = {
            'citation': '',
            'description': '',
            'filename': '',
            'name': '',
            'resource_type': 'Data_Set',
            'the_publication': False
        }
        print self.allfiles
        metadata = [dict(default_meta)
                    for f in self.allfiles] # if f not in self.exceptfiles]
        return metadata
    
# update({'filename': f, 'name': f})
        
              

# def checkargs():
#     p = Parser()
#     print p.parse(sys.argv)

# #checkargs()

# args = {'subcmd': 'put', 'pkg_name': 'test-the-bulk-upload', 'keepdummy': False,
#         'directory': '/home/vonwalha/tmp/test_resup', 'tar': False, 'gz': False}
pa = Parser()
args = pa.parse(sys.argv)
put =Put(args)


# put = Put(args)


# if __name__ == '__main__':
#     pass
    



with open('/home/vonwalha/tmp/test_resup/metadata.yaml', 'r') as f:
    test = yload(f)



