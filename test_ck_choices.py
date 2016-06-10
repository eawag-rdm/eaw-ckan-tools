from ck_choices import *
from nose.tools import *
import os
import json
import copy
from mock import patch, call


def test_mkparser():
    parser = mkparser()
    assert_equal(vars(parser.parse_args([
        '--del','--resource', 'Field', 'term1', 'term2'])),
                 {'del':True, 'field': 'Field', 'resource': True,
                  'terms': ['term1', 'term2']})
    
def test_load_schema():
    obj = {'att1': ['1', 2, '3',4]}
    with open('testschema', 'wb') as f:
        json.dump(obj, f)
    res = load_schema('testschema')
    assert_equal(obj, res)
    os.remove('testschema')
    with open('testschema', 'wb') as f:
        f.write('this ain\'t json')
    with assert_raises(SystemExit) as cm:
        load_schema('testschema')
    assert_equal(cm.exception.args,
                 ("Schema file testschema doesn't parse into JSON",1))
    os.remove('testschema')
    with assert_raises(SystemExit) as cm:
        load_schema('testschema')
        assert_equal(cm.exception.args,
                     ("Could not open schema file 'testschema'",1))

def test_update_field():

    testschema = {'dataset_fields': [
        {"field_name": "variables",
         "label": "Variables",
         "choices": [
	     {"value": "alkalinity",
	      "label": "alkalinity"
	     },
	     {"value": "degradation_rate",
	      "label": "degradation Rate"
             }]},
        {"field_name": "varibums",
         "label": "Variables",
         "choices": [
	     {"value": "alkalinity",
	      "label": "alkalinity"
	     },
	     {"value": "degradation_rate",
	      "label": "degradation Rate"
             }]}
        ],
        'resource_fields': [
            {"field_name": "variables",
             "label": "Variables",
             "preset": "multiple_select_js",
             "choices": [
	         {"value": "resalkalinity",
	          "label": "resalkalinity"
	         },
	         {"value": "resdegradation_rate",
	          "label": "resdegradation Rate"
                 }]}
        ]}

    # add 2 terms to dataset_fields
    retest = copy.deepcopy(testschema)
    retest['dataset_fields'][1]['choices'].extend([{"value": 'new_value_1',
                                                    'label': 'New Value 1'},
                                                   {'label': 'New Value 2',
                                                    'value': 'new_value_2'}])
    res = update_field(testschema, 'dataset_fields', 'varibums', False, [
        ('new_value_1', 'New Value 1'), ('new_value_2','New Value 2')])
    assert_equal(retest, res)
    # remove terms
    retest = copy.deepcopy(testschema)
    retest['dataset_fields'][0]['choices'] = []
    res = update_field(testschema, 'dataset_fields', 'variables', True, [
        'degradation_rate', 'alkalinity'])
    assert_equal(retest, res)
    # non-existing field
    with assert_raises(SystemExit) as cm:
        res = update_field(testschema, 'dataset_fields', 'variables_not', True, [
        'degradation_rate_not', 'alkalinity'])
        assert_equal(cm.args, ('Could not find field "variables_not" ' +
                               'in "dataset_fields"', 1))
    # non existing typ
    with assert_raises(SystemExit) as cm:
        res = update_field(testschema, 'dataset_fields_not', 'variables_not',
                           False, ['degradation_rate_not', 'alkalinity'])
        assert_equal(cm.args,
                     ('Could not find field_type "dataset_fields_not"', 1))

@patch('ck_choices.argparse.ArgumentParser')
def test__postparse(parser):
    elist = []
    print_help_calls = []
    p = []
    for dele in [True, False]:
        for terms in [
                ['aa,bb', 'oo,pp'],
                ['aa,bb', 'oopp'],
                ['aabb', 'oopp'],
                ]:
            params = {'terms': terms, 'del': dele}
            try:
                pp = postparse(params, parser)
            except SystemExit as e:
                print_help_calls.extend(parser.method_calls)
                parser.reset_mock()
                elist.append(e.code)
                p.append(False)
            else:
                print_help_calls.append(False)
                elist.append(False)
                p.append(pp)
    assert_equal(print_help_calls,
                 [call.print_help(), call.print_help(), False, False,
                  call.print_help(), call.print_help()])
    assert_equal(p, [False, False, ['aabb', 'oopp'],
                     [('aa', 'bb'), ('oo', 'pp')],
                     False, False])
    assert_equal(elist, [1, 1, False, False, 1, 1])

def test_check_unique():
    field = 'the_field'
    choices = [{'value': 'val1', 'label': 'lab1'},
               {'value': 'val2', 'label': 'lab2'}]
    with assert_raises(SystemExit) as cm:
        check_unique(field, choices,
                     [('val1', 'Label1'),('val3', 'Label3')])
    assert_equal(cm.exception.args, ('val1 already in the_field',))
    check_unique(field, choices,
                     [('val3', 'Label1'),('val4', 'Label3')])
