#!/usr/bin/env python

# HvW - 2016-06-15
# transformation of coordinates from textarea
# iterative development along real use cases
# 1. Anze's degree / minutes / seconds


import re
import sys
import json
from decimal import *
getcontext().prec = 8


class Coordparser(object):

    def __init__(self):
        self.txt = ''
        self.points = []
        self.geojson = ''
        return

    # values are multipliers
    directions = {'N': 1, 'E': 1, 'S': -1, 'W': -1}
    dir_sig = ur'(?P<direction>[' + ''.join(directions.keys()) + ']?)'
    deg_sig = ur'°'
    min_sig = ur'`'
    sec_sig = ur'``'
    deg_pat = (ur'\s*' + dir_sig + ur'?\s*' + ur'(?P<degs>\d{1,3})\s*' +
               deg_sig + ur'\s*')
    min_pat = ur'\s*(?P<mins>[0-5]?\d)\s*' + min_sig + ur'\s*'
    sec_pat = ur'\s*(?P<secs>[0-5]?\d(?:\.\d*)?)\s*' + sec_sig + ur'\s*'

    regex = re.compile(deg_pat + min_pat + sec_pat, re.I|re.U)

    # read textarea input from file
    def get_from_file(self, filename):
        with open(filename, 'r') as f:
            self.txt = f.read()
        return(self)

    # parses one line for first coordinate
    def _parse(self, coostring):
        parseres = re.match(self.regex, coostring)
        if not parseres:
            sys.exit("Unable to decode coordinates")
        return((parseres.groupdict(), parseres.group(0)))

    # transforms on dms - coordinate
    # ({'direction': , 'degs': ,'mins': ,'secs': }) to decimal
    def _dms2decimal(self, dmsdict):
        point0 = dmsdict
        factor = self.directions[point0['direction']]

        #print type(point0['degs'])
        # print Decimal(point0['mins'])
        # print Decimal('60')
        # print Decimal(point0['secs'])
        # print Decimal('3600')

        
        point_dec = Decimal(factor) * (
            Decimal(point0['degs']) + Decimal(point0['mins']) / Decimal('60') +
            Decimal(point0['secs']) / Decimal('3600'))
        return(point_dec)

    # parses textarea
    # returns list of points
    def textarea2points(self):
        points = []
        lines = [s.strip()for s in self.txt.splitlines()]
        for l in lines:
            pdict = {}
            lp = l
            for p in ('y', 'x'):
                dmsdict, match = self._parse(lp)
                pdict[p] = self._dms2decimal(dmsdict)
                lp = lp.replace(match, '')
            points.append(pdict)
        self.points = points
        return(self)

    # converts list of points (in decimal degrees) to geojson geometry
    # typ is one of: "Point", "MultiPoint", "LineString",
    #                "Polygon", "MultiPolygon"
    def points2geojson(self, typ):
        geoj = {'type': typ, 'coordinates': []}
        if typ == 'Point':
            assert(len(self.points) == 1)
            geoj['coordinates'] = [self.points[0]['y'], self.points[0]['x']]
        elif typ in ['MultiPoint', 'LineString', 'Polygon']:
            assert(len(self.points) > 1)
            geoj['coordinates'] = [[float(p['x']), float(p['y'])]
                                   for p in self.points]
        else:
            sys.exit('GeoJSON type "{}" is net (yet) implemented'.format(typ))
        self.geojson = json.dumps(geoj) 
        return(self)
        
    
from nose.tools import *

class Test_Coordparser(object):
    
    def __init__(self):
        self.setUp()
    
    def setUp(self):
        self.P = Coordparser()
    
    def _test_pat(self, patstr, test, expect):
        for idx, t in enumerate(test):
            pat = re.compile(patstr, re.I|re.U)
            degs = re.match(pat, t)
            if degs:
                assert_equals(degs.groupdict(), expect[idx])
            else:
                assert(expect[idx] is False)

    def test_deg_pat(self):
        patstr = self.P.deg_pat
        test = [u'N47° ', u'  N47°', u'N47°']
        expect = [{'direction': 'N', 'degs': '47'}]*3
        self._test_pat(patstr, test, expect)

    def test_min_pat(self):
        patstr = self.P.min_pat
        test = [u'16` ', u' 16 `', u' 8`']
        expect = [{'mins': '16'}]*2 + [{'mins':'8'}]
        self._test_pat(patstr, test, expect)

    def test_sec_pat(self):
        patstr = self.P.sec_pat
        test = [u'88.3`` ', u' 6.9635 ``',  u'59``']
        expect = [False, {'secs': u'6.9635'}, {'secs': u'59'}]
        self._test_pat(patstr, test, expect)

    def test_textarea2points(self):
        self.P.txt = \
"""N47°   16` 52``  E8° 48` 36``
N47° 16`  54``  E8°  46` 49``
N47° 18` 8`` E8° 44`  52``
N47° 18`  10`` E8° 44` 47``
N47° 19` 6`` E8° 42` 54``
N47° 19` 46``  E8° 43` 2``
"""
 
        expect = [{'y': Decimal('47.281111'), 'x': Decimal('8.81')},
                  {'y': Decimal('47.281667'), 'x': Decimal('8.7802778')},
                  {'y': Decimal('47.302222'), 'x': Decimal('8.7477777')},
                  {'y': Decimal('47.302778'), 'x': Decimal('8.7463889')},
                  {'y': Decimal('47.318334'), 'x': Decimal('8.715')},
                  {'y': Decimal('47.329445'), 'x': Decimal('8.7172223')}]

       
        self.P.textarea2points()
        eq_(self.P.points, expect)
        
        
                  
# Test_Coordparser().test_deg_pat()
# Test_Coordparser().test_min_pat()
# Test_Coordparser().test_sec_pat()
# Test_Coordparser().test_textarea2points()

P = Coordparser()
#

out = (P.get_from_file('coordinates.txt').textarea2points()
       .points2geojson('MultiPoint').geojson)
print out
