import logging
import urllib2

from django.utils import simplejson

logger = logging.getLogger(__name__)

try:
	from getty.settings import FLICKR_API_KEY as api_key
except ImportError:
	api_key = None
	
class NoHits(Exception):
	pass

class ApiKeyNotSet(Exception):
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
		try:
			self.json_response = urllib2.urlopen(request)		
		except urllib2.URLError, msg:
			logger.error("Couldn't contact Flickr: %s" % msg)
			self.json_response = None
			
	def parse_json_to_dict(self):
		'''Given a JSON response from Flickr,
		parse the result into a dict.'''
		try:
			json_str = self.json_response.read()
			self.photo_dict = simplejson.loads(json_str)['photos']['photo'][0]
		except IndexError:
			logger.warning("No Flickr search result for keyword: %s" % self.keyword)
			raise NoHits
		except Exception, msg:
			logger.error("Couldn't parse JSON: %s: %s" % (Exception, msg))
			logger.error("%s" % json_str)
			self.photo_dict = None
			
	def get_url(self):
		'''Given a dict of its properties, construct
		the appropriate URL for the photo.'''
		host = "http://farm%s.static.flickr.com/" % self.photo_dict['farm']
		self.url = host + "%s/%s_%s_%s.jpg" % (self.photo_dict['server'],
											    self.photo_dict['id'],
											    self.photo_dict['secret'],
												self.size)		