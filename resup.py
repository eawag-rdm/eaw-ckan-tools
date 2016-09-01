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
        pa_put.add_argument('dir', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='The top-level directory containing the ressources '+
                        'to be uploaded. Default is the current working directory.')
        pa_put.add_argument('-tar', action='store_true', help='create a tar archive')
        pa_put.add_argument('-gz', action='store_true', help='gzip the file(s) before upload')
        
        # get subcommand
        pa_get = subparsers.add_parser('get', help='download ressources')
        pa_get.add_argument('pkg_name', metavar='PACKAGENAME', type=str,
                        help='Name of the data package')
        pa_get.add_argument('dir', metavar='DIRECTORY', type=str, nargs='?',
                        default=os.curdir,
                        help='Directory into which ressources are downloaded. ' +
                        'Default is the current working directory.')
        # list subcommand
        pa_list = subparsers.add_parser('list', help='list your packages')
        
    def parse(self, arglist):
        arguments = vars(self.pa.parse_args())
        return arguments

p = Parser()
args = p.parse(sys.argv)

print args
# print pa.parse_args(['get', 'direc'])
# 


