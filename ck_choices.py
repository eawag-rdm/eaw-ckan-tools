#!/usr/bin/env python

"""
makes modifications to the controlled vocabulary (implemented as
ckanext-scheming "choices")
HvW - 2016-06-07
"""

import ckanapi
import argparse
import sys
import json
import pprint
import os

LOCAL_SCHEMA=("/usr/lib/ckan/default/src/ckanext-eaw_schema/ckanext/" +
               "eaw_schema/eaw_schema_default.json")
    
def mkparser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=
"""
Make modifications to the controlled vocabulary \"field\"
(implemented as ckanext-scheming "choices").
""",                                  epilog=
"""
Examples:
ck_choices.py variables "new_var_1,New Variable One" newvar2,"Another One"
adds two new terms to the dataset_field "variables".

ck_choices.py variables --del new_var_1 newvar2
deletes them.
"""
    )
    parser.add_argument('field', help='the schema field to be modified',
                        metavar='FIELD')
    parser.add_argument('--del', action='store_true', help='delete terms '+
                        '(default is adding terms)')
    parser.add_argument('--resource', action='store_true', help='action ' +
                        'refers to resource field (default is dataset field)') 
    parser.add_argument('terms', nargs='+', help='the terms to be added '
                        +'(removed). Have the format "value,label" for adding,' +
                        ' and "value" for removing', metavar='TERM')
    return(parser)


def postparse(params, parser):
    terms = params['terms']
    terms = [tuple(x.split(',')) for x in terms]
    if params['del'] and not all([len(x) == 1 for x in terms]):
        parser.print_help()
        sys.exit(1)
    elif not params['del'] and not all([len(x) == 2 for x in terms]):
        parser.print_help()
        sys.exit(1)
    terms = [x[0] if len(x) == 1 else x for x in terms]
    return(terms)
    

def load_schema(schemafile):
    try:
        with open(schemafile) as sf:
            schema = json.load(sf)
    except ValueError:
        raise(SystemExit("Schema file {} doesn't parse into JSON"
                         .format(schemafile), 1))
    except IOError:
        raise(SystemExit("Could not open schema file 'testschema'", 1))
    return(schema)

def check_unique(field, choices, terms):
    for t in [x[0] for x in terms]:
        if t in [x['value'] for x in choices]:
            raise SystemExit('{} already in {}'.format(t, field))

def update_field(schema, typ, field, remove, terms):
    " typ: 'dataset_field' or 'resource_field'"
    def _build_choices(terms):
        ch = [{'value': t[0], 'label': t[1]} for t in terms]
        return ch
        
    def _get_val_index(val, choices):
        idx = [x.get('value') for x in choices].index(val)
        return(idx)
    try:
        f = [x for x in schema[typ] if x["field_name"] == field]
    except KeyError:
        raise SystemExit('Could not find field_type "{}"'.format(typ))
    if not f:
        raise SystemExit("Could not find field \"{}\" in \"{}\""
                         .format(field, typ))
    assert(len(f) == 1)
    c = f[0]['choices']
    if not remove:
        check_unique(field, c, terms)
        c.extend(_build_choices(terms))
    else:
        try:
            rmidx = [_get_val_index(val, c) for val in terms]
        except ValueError:
            raise SystemExit('Not all terms found in ' +
                             'field "{}" in "{}"'.format(field, typ))
        if len(rmidx) < len(terms):
            raise SystemExit('Not all terms found in ' +
                 'field "{}" in "{}"'.format(field, typ))
        cnew = [x[1] for x in enumerate(c) if x[0] not in rmidx]
        f[0]['choices'] = cnew
    return(schema)

def write_schema(newschema, path):
    with open(path, 'w') as f:
        json.dump(newschema, f, indent=2)
        
def main():
    parser = mkparser()
    params = vars(parser.parse_args())
    terms = postparse(params, parser)
    field = params['field']
    remove = params['del']
    typ = 'resource_fields' if params['resource'] else 'dataset_fields'
    schema = load_schema(LOCAL_SCHEMA)
    newschema = update_field(schema, typ, field, remove, terms)
    write_schema(newschema, LOCAL_SCHEMA)

if __name__ == '__main__':
    main()



