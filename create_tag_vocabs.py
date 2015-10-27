#!/usr/bin/env python

###############################################################
#
# Create tag vocabularies for Eawag Research Data Platform
# HvW - 2015-10-27
#
###############################################################

import os
import sys
import re
import argparse
from pprint import PrettyPrinter
import ckanapi

pp = PrettyPrinter(indent = 2)

host = "http://localhost:5000"
apikey = os.environ['CKAN_APIKEY_HVW_ADM']
ckan = ckanapi.RemoteCKAN(host, apikey=apikey)

# not used, currently
def sanitize_name(name):
    name_san = re.sub('[^0-9a-zA-Z]+', '-', name).lower()
    return(name_san)

def new_vocab(vocab_name, tag_file):
    ## check whether we already have that vocabulary name
    try:
        vocab = ckan.call_action('vocabulary_show', {'id': vocab_name})
        print("Vocabulary {} exists:".format(vocab_name))
        pp.pprint(vocab)
        return(2)
    except ckanapi.NotFound:
        with open(tag_file) as f:
            tagnames = [x.strip('\n') for x in f.readlines()]
        #tag_names = [sanitize_name(x) for x in tag_disp_names]
        vocab = ckan.call_action('vocabulary_create', {'name': vocab_name})
        for t in tagnames:
            ckan.call_action('tag_create', {'name': t, 'vocabulary_id': vocab['id']})
        vocab = ckan.call_action('vocabulary_show', {'id': vocab['id']})
        print("Created vocabulary {}:".format(vocab['name']))
        pp.pprint(vocab)

def del_all_vocabs():
    vocabs = ckan.call_action('vocabulary_list')
    vocabids = [x['id'] for x in vocabs]
    for id in vocabids:
        # delte all tags
        vocab = ckan.call_action('vocabulary_show', {'id': id})
        for tid in [x['id'] for x in vocab['tags']]:
            ckan.call_action('tag_delete', {'id': tid, 'vocabulary_id': id})
        # delete vocabulary
        ckan.call_action('vocabulary_delete', {'id': id})

def show_vocabs():
    vocablist = ckan.call_action('vocabulary_list')
    pp.pprint(vocablist)
    # for voc in vocablist:
    #     ckan.call_api('vocabulary_show', voc['id'])

def cli_parse():
    parser = argparse.ArgumentParser(description='Create tag-vocabulary')
    parser.add_argument('--clean', help='remove all tag-vocabularies first',
                        action='store_true')
    parser.add_argument('vocnam', metavar='vocabulary_name', nargs='?')
    parser.add_argument('vocdef', metavar='vocabuary_definition', nargs='?',
                        help='file containing a tag name in each line')
    parser.add_argument('--show', help='only show vocabularies',
                        action='store_true')
    args = vars(parser.parse_args())
    if (not args['show']) and (not (args['vocnam'] and args['vocdef'])):
        print("Too few arguments")
        parser.print_help()
        sys.exit(0)
    return(args['vocnam'], args['vocdef'], args['clean'], args['show'])

    
if __name__ == '__main__':
    vocabname, vocabdeffile, clean, show = cli_parse()
    if show:
        show_vocabs()
        sys.exit(0)
    else:
        if not (vocabname and vocabdeffile):
            print("Too few arguments")
            p
        print(vocabname, vocabdeffile, clean, show)
        sys.exit(0)
        if clean:
            del_all_vocabs()
        new_vocab(vocabname, vocabdeffile)
        show_vocabs()
