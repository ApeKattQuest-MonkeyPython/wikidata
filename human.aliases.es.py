#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time

import pwb
import pywikibot
from wikidatafun import *

def main():
    targetlang = 'es'
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    countries = [ #only Spanish language countries
        'Q414', #Argentina
        'Q750', #Bolivia
        'Q298', #Chile
        'Q739', #Colombia
        'Q800', #Costa Rica
        'Q241', #Cuba
        'Q786', #Dominican Republic
        'Q736', #Ecuador
        'Q792', #El Salvador
        'Q774', #Guatemala
        'Q783', #Honduras
        'Q96',  #Mexico
        'Q811', #Nicaragua
        'Q804', #Panama
        'Q733', #Paraguay
        'Q419', #Peru
        'Q29',  #Spain
        'Q77',  #Uruguay
        'Q717', #Venezuela
    ] 
    for country in countries:
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3A'+country+'.%0A%7D'
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            print('==', q, '==')
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            aliases = item.aliases
            labels = item.labels
            if not targetlang in labels:
                print('Not label %s found' % (targetlang))
                continue
            
            names = [labels[targetlang]]
            if targetlang in aliases:
                [names.append(x) for x in aliases[targetlang]]
            
            plainnames = []
            for name in names:
                if not 'ñ' in name.lower() and \
                    not 'ç' in name.lower():
                    #avoid producing names Carlos I de España->Espana
                    plainnames.append(removeAccents(name))
            
            missingnames = []
            for plainname in plainnames:
                if not plainname.lower() in [x.lower() for x in names] and \
                   not plainname.lower() in [y.lower() for y in missingnames]:
                    if targetlang in aliases.keys():
                        aliases[targetlang].append(plainname)
                    else:
                        aliases[targetlang] = [plainname]
                    missingnames.append(plainname)
            
            if missingnames:
                data = { 'aliases': aliases }
                missingnames.sort()
                summary = "BOT - Adding aliases (%s in %s language): %s" % (len(missingnames), targetlang, ', '.join(missingnames))
                print(summary)
                try:
                    item.editEntity(data, summary=summary)
                except:
                    print('Error while saving')
                    continue
    
    print("Finished successfully")
        
if __name__ == "__main__":
    main()