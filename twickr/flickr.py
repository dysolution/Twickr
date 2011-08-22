import logging
import urllib2

from django.utils import simplejson

try:
	from getty.settings import FLICKR_API_KEY as api_key
except ImportError:
	api_key = None
	
class NoHits(Exception):
	pass

class ApiKeyNotSet(Exception):
	pass
	
class UnknownFlickrError(Exception):
	pass
	
class Photo():
	def __init__(self, api_key=api_key, keyword=None, url=None, size=None):
		'''Given a keyword, query Flickr for the first matching photo.
		Default is the medium (240 px on longest side) size.'''
		if not api_key:
			raise ApiKeyNotSet
			
		self.keyword = keyword
		if size not in ['m','s','t','z','b']:
			self.size = 'm'
		else:
			self.size = size
			
		self.url = url
		self.photo_dict = None
			
		if self.keyword:
			self.query_flickr()
			self.parse_json_to_dict()
			if self.photo_dict:
				self.get_url()
		
	def query_flickr(self):
		'''Query the Flickr API and get a JSON response.'''
		self.request_url = 'http://api.flickr.com/services/rest/?method=flickr.photos.search'
		api_params = {
			'format': 'json',
			'nojsoncallback': '1',
			'media': 'photos',
			'per_page': '1',
			'api_key': api_key,
			'text': self.keyword,			
			}
		for param, value in api_params.iteritems():
			self.request_url += "&%s=%s" % (param, value)
		request = urllib2.Request(self.request_url)
		logging.debug("Flickr query URL: %s" % self.request_url)
		try:
			self.json_response = urllib2.urlopen(request)		
		except urllib2.URLError, msg:
			logging.error("Couldn't contact Flickr: %s" % msg)
			self.json_response = None
			
	def parse_json_to_dict(self):
		'''Given a JSON response from Flickr,
		parse the result into a dict.'''
		self.json_str = self.json_response.read()
		self.response_dict = simplejson.loads(self.json_str)
		if self.response_dict['stat'] == 'ok':
			if self.response_dict['photos']['total'] == '0':
				logging.warning("No Flickr search result for keyword: %s" % self.keyword)
				raise NoHits
			else:
				self.photo_dict = self.response_dict['photos']['photo'][0]
		elif self.response_dict['stat'] == 'fail':
			if self.response_dict['code'] == 100:
				logging.critical('Twitter response: %s' % self.response_dict)
				logging.critical('Please set a valid Flickr API key in settings.py.')
				raise ApiKeyNotSet
			else:
				print self.response_dict
				raise UnknownFlickrError
			
	def get_url(self):
		'''Given a dict of its properties, construct
		the appropriate URL for the photo.'''
		host = "http://farm%s.static.flickr.com/" % self.photo_dict['farm']
		self.url = host + "%s/%s_%s_%s.jpg" % (self.photo_dict['server'],
											    self.photo_dict['id'],
											    self.photo_dict['secret'],
												self.size)		