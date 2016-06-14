#!/usr/bin/env python
# encoding: utf-8
# Author: Weston Ruter (@westonruter) http://weston.ruter.net/
# CLI usage: cat coordinates.txt | python coordinates.py
# https://gist.github.com/westonruter/4685648

import sys
import re
from decimal import Decimal

def normalize_coordinate(c):
    matches = re.match(
        ur'''
        (?P<degs>-?\d+(?:\.\d+)?)[°]?
        (?:\s*(?P<mins>\d+(?:\.\d+)?)[\'′]
            (?:\s*(?P<secs>\d+(?:\.\d+)?)["″])?
        )?
        \s*
        (?P<dir>[NSEW])?
        ''',
        c, re.U | re.X | re.I
    )
    if matches:
        groups = matches.groupdict('0')
        degs = Decimal(groups['degs'])
        mins = Decimal(groups['mins'])
        secs = Decimal(groups['secs'])
        c = degs + mins/60 + secs/3600
        if groups['dir'].upper() in (u'W', u'S'):
            c = -c
    else:
        c = Decimal(c)
    return c

def parse_coordinates(coordinates):
    (lat, lon) = re.split(r',\s*|(?<=[NSEW]) ', cc)
    lat = normalize_coordinate(lat)
    lon = normalize_coordinate(lon)
    return (lat, lon)

if __name__ == '__main__':
    for coordinates in sys.stdin:
        cc = unicode(coordinates.strip(), 'utf-8')
        if len(coordinates) == 0:
            continue
        (lat, lon) = parse_coordinates(coordinates)
        print '%s,%s' % (lat, lon)



coo = u"N47° 16`"# 52\""

parser = re.compile(ur"""
                    [NSWE]\s*\d+°\s*\d+`  #\s*\d+``
                    """, re.VERBOSE|re.UNICODE)

res = re.match(parser, coo)
print res


