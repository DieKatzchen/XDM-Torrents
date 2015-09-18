# Author: DieKatzchen
# URL: https://github.com/DieKatzchen/XDM-Torrents
#
# This file is part of XDM: eXtentable Download Manager.
#
# XDM: eXtentable Download Manager. Plugin based media collection manager.
# Copyright (C) 2013  Dennis Lutter
#
# XDM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# XDM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from xdm.plugins import *
import urllib
import logging
from xdm import helper
from xml.dom.minidom import parseString
from xml.dom.minidom import Node
import unicodedata
import re
from requests import RequestException

log = logging.getLogger('kat')

def isValidItem(terms,  title):
    for term in terms.split('+'):
        if not (term in title):
            return False
    return True
    
    

#class SearchKAT(object):
#    schema = {
#        'type': 'object',
#        'properties': {
#            'category': {'type': 'string', 'enum': ['all', 'movies', 'tv', 'music', 'books', 'xxx', 'other']},
#            'verified': {'type': 'boolean'}
#        },
#        'additionalProperties': False
#    }

class KAT(Indexer):
	version = "0.001"
	identifier = "en.diekatzchen.kat"
	
	types = ['de.lad1337.torrent']
	
	def _baseUrlRss(self, search):
		return "https://kat.cr/usearch/{}/".format(search)
	
	def searchForElement(self, element):
		payload = { 'rss' : 1 }
		downloads = []
		terms = element.getSearchTerms()
		for term in terms:
			url = _baseUrlRss(term)
			try:
				r = requests.get(url, params=payload, raise_status=False)
			except RequestException as e:
				log.warning('Search resulted in: {}'.format(e))
				continue
			if not r.content:
				log.debug('No content returned from search.')
				continue
			elif r.status_code != 200:
				log.warning('Search returned {} response code'.format(r.status_code))
				continue
			rss = feedparser.parse(r.content)
			
			ex = rss.get('bozo_exception', False)
			if ex:
				log.warning('Got bozo_exception (bad feed)')
				continue
			for item in rss.entries:
				title = item.title
				if not item.get('enclosures'):
					log.warning('Could not get url for entry from KAT. Maybe plugin needs updated?')
					continue
				if isValidItem(element.getName(), title):
					url = item.enclosures[0]['url']
					
					d = Download()
					d.url = url
					d.name = title
					d.element = element
					d.size = item.torrent_contentLength
					d.external_id = getTorrentExternalId(url)
					d.type = 'de.lad1337.torrent'
					downloads.append(d)
					
		if len(downloads) == 0:
			log.info("No search results for {}.".format(terms))
				
		return downloads
		
def getConfigHtml(self):
    return """<script>
        function newsznab_""" + self.instance + """_spreadCategories(data){console.log(data);
          $.each(data, function(k,i){
          $('#""" + helper.idSafe(self.name) + """ input[name$="'+k+'"]').val(i)
          });
        };
        </script>
    """
    
config_meta = {'plugin_desc': 'Quick and dirty KAT indexer'}