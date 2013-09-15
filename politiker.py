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

import twitter
from lxml.html.soupparser import fromstring





def alert(x):
    print x+'\n\n'+u' quitting!'
    sys.exit(-1)
firsts = lambda xs: [x[0] for x in xs]

# this URL may or may not expire at some point…
html = scraperwiki.scrape("http://www.parlament.gv.at/WWER/NR/filterRearrange.psp?R_WF=FR&WP=ALLE&FUNK=ALLE&requestId=0F02FED9BB&M=M&LISTE=&WK=ALLE&NRBR=NR&FR=ALLE&W=W&STEP=1000&listeId=2&GP=AKT&R_PBW=PLZ&pageNumber=&FBEZ=FW_002&PLZ=&xdocumentUri=%2FWWER%2FNR%2Findex.shtml&BL=ALLE&jsMode=")
root = fromstring(html)

tables = root.cssselect('table')

if len(tables) < 1:
    alert('no table found!')
if len(tables) > 1:
    alert('more than one table found!')

table = tables[0]

rows = table.cssselect('tr')

rows = rows[1:]


abgeordnete = []

for row in rows:
    rowcols = row.cssselect('td')
    link = rowcols[0].cssselect('a')[0].get('href')
    name = rowcols[0][0][0].tail.strip()
    abgeordnete.append({'name': name, 'link': link, 'wahlkreis': row[2].text.strip(), 'fraktion': row[1][0].text, 'bundesland': row[3][0].text})

for abgeordnet in abgeordnete:
    html2 = scraperwiki.scrape('http://www.parlament.gv.at/'+abgeordnet['link'])
    root2 = lxml.html.fromstring(html2)
    contact = root2.cssselect('.linkeSpalte40 .grauBox p a')
    contact_links = [a.get('href') for a in contact]
    email_candidates = [re.findall('[^\s]*@[^\s]*', x) for x in contact_links]
    email_candidates = [x.replace('mailto:','') for x in list(itertools.chain(*email_candidates))]
    abgeordnet['email'] = email_candidates

    detaillists = root2.cssselect('#content .contentBlock.h_1 ul li')
    detailitem = [x for x in detaillists if x.text and 'zum Nationalrat' in x.text]
    bezeichnung = detailitem[0].text
    gender = 'm' if 'Abgeordneter' in bezeichnung else 'w'
    abgeordnet['gender'] = gender

for abgeordnet in abgeordnete:
    headers = ['Name', 'Link', 'Wahlkreis', 'Fraktion', 'Bundesland', 'Gender']
    for x in xrange(0, len(abgeordnet['email'])):
        headers += ['Email%s' % (x+1)]
    savethings = [abgeordnet['name'], abgeordnet['link'], abgeordnet['wahlkreis'], abgeordnet['fraktion'], abgeordnet['bundesland'], abgeordnet['gender']]
    for x in abgeordnet['email']:
        savethings += [x]
    datadict = dict(zip(headers, savethings))
    scraperwiki.sqlite.save(headers, datadict)
