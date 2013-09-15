#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pdb
import scraperwiki
import lxml.html
import sqlite3
import json
import datetime
import logging
import logging.handlers
import re
import itertools
import lxml.etree as etree

from lxml.html.soupparser import fromstring

# this URL may or may not expire at some point…
html = scraperwiki.scrape("http://www.parlament.gv.at/PAKT/VHG/XXIV/NRSITZ/NRSITZ_00215/index.shtml")
root = fromstring(html)

tables = root.cssselect('table.tabelle.tabelleHistorie')

for table in tables:
    if "Redner" in table.attrib['summary']:
        for tr in table.cssselect('tr') :
            a = tr.cssselect('a')
            if a :
                name = [t for t in a[0].itertext()][0]
                partei = re.findall('\(([A-Z]+)\)', name)[0]
                zeit = tr.cssselect('td')[6].text.strip()
                data = dict(name = name, partei = partei, zeit = zeit)
                print data
                scraperwiki.sqlite.save(["name", "partei", "zeit"], data)
