import logging
import urllib2

from django.utils import simplejson

logger = logging.getLogger(__name__)

try:
	from getty.settings import FLICKR_API_KEY as api_key
except ImportError:
	api_key = None
	fatal_error = "Unable to determine the Flickr API key. Please set it in settings.py."

class NoHits(Exception):
	pass

def get_photo_url(keyword, api_key=api_key):
	'''Return the URL of the "medium"-sized version of the first photo
	found when the keyword is provided to the flickr.photos.search
	method of the Flickr API. Return None if something goes wrong with
	the search.'''
	if keyword is None:
		logging.warning('No keyword provided.')
		return None
	else:
		logging.info('Keyword: %s' % keyword)
		
	if api_key is None:
		logging.error('No API key provided.')
		return None

	try:
		request_url = 'http://api.flickr.com/services/rest/?api_key=%s&method=flickr.photos.search&format=json&nojsoncallback=1&media=photos&per_page=1&text=%s' % ( api_key, keyword )
		request = urllib2.Request(request_url)
		json_response = urllib2.urlopen(request)		
	except urllib2.URLError, msg:
		logger.error("Couldn't contact Flickr: %s" % msg)
		return None		
	try:
		json_str = json_response.read()
		photo = simplejson.loads(json_str)['photos']['photo'][0]
	except IndexError:
		logger.warning("No Flickr search result for keyword: %s" % keyword)
		raise NoHits
	except Exception, msg:
		logger.error("Couldn't parse JSON: %s: %s" % (Exception, msg))
		logger.error("%s" % json_str)
		return None
	photo_url_medium = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (photo['farm'], photo['server'], photo['id'], photo['secret'])
	return photo_url_medium
