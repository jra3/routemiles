"""
Scraper script to find airport coordinates.
No longer needed with airports.kml
"""
import itertools
import string
import simplejson
import urllib2
import sys
import re

url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s+airport&sensor=true"

def process_result(code, info):
    if info['status'] != 'OK':
        return None
    for result in info['results']:
        if 'airport' not in result['types']:
            print "not an airport"
            continue
        out =  result['geometry']['location']
        out['code'] = code
        return out
    return None


codes = [''.join(x) for x in  itertools.product(string.uppercase, repeat=3)]
for code in codes:
    code = code.strip()
    info = simplejson.load(urllib2.urlopen(url % (code,)))
    print process_result(code, info)
