import urllib2
			  
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.shortcuts import render_to_response
from django.template import RequestContext

fatal_error = None

import logging
logger = logging.getLogger(__name__)

try:
	from getty.settings import FLICKR_API_KEY as api_key
except ImportError:
	api_key = None
	fatal_error = "Unable to determine the Flickr API key. Please set it in settings.py."
from getty.twickr.models import Search

class NoHits(Exception):
	pass

class Tweet():

	def __init__(self, author=None, text=None, parsed_response=None,
				 json=None):
		'''Query Twitter for a tweet and parse the response to 
		extract its author and its text.
		
		For testing purposes, a manufactured tweet can be provided in several forms:
		
		1. just an author and some text
		2. a dict in the same format that the JSON parsing would provide
		3. raw JSON in the same format that Twitter returns
		'''
		self.author = author
		self.text = text
		self.json = json
		self.parsed_response = parsed_response
			
		if not self.json:
			self.get_latest_json()
			
		if not self.parsed_response:
			self.parse_json()
			
		if not self.text:
			self.author = self.parsed_response['user']['screen_name']
			self.text = self.parsed_response['text']
		
		self.get_words()
		self.get_keyword()
	
	def get_latest_json(self):
		'''Query the Twitter public timeline without
		passing OAuth credentials to get a JSON response.'''
		query_url='http://api.twitter.com/1/statuses/public_timeline.json?count=1'
		request = urllib2.Request(query_url)
		try:
			self.json = urllib2.urlopen(request)
		except urllib2.URLError, msg:
			logger.error("Couldn't contact Twitter: %s" % msg)
			self.json = None
			
	def parse_json(self):
		'''Parse the JSON into a dict with the tweet
		properties as keys.'''
		try:
			self.parsed_response = simplejson.load(self.json)[0]	
		except Exception, msg:
			logger.error("Couldn't parse JSON: %s: %s" % (Exception, msg))
			self.parsed_response = None
			
	def get_words(self):
		'''Words are defined as the tokens created when the tweet is
		split on whitespace.'''
		if self.text:
			# Sanitize the words further here if desired.
			self.words = self.text.split()
		else:
			self.words = []
			
	def get_keyword(self):
		'''Starting with the 3rd word in the tweet,
		find the first acceptable word.'''
		if len(self.words) < 3:
			logging.warning('Not enough words in phrase. Words: %s' % self.words)
			self.keyword = None
		else:				
			good_word = None
			for x in range(2, len(self.words)):
				if Word(self.words[x]).is_acceptable():
					good_word = self.words[x]					
					break
			if good_word:
				self.keyword = good_word
			else:
				logging.warning('No acceptable keyword found in tweet.')
				self.keyword = None

class Word():
	def __init__(self, content):
		self.content = content
		
	def is_acceptable(self):
		'''Defines criteria under which a word will be acceptable
		as a keyword with which to search Flickr.
		
		Sanitize the word before it's used as a query on Flickr
		by adding additional elif statements here if desired.'''
		try:
			# We only want simple ASCII keywords.
			self.content.encode('ascii')
		except UnicodeEncodeError:
			return False
			
		if self.content.lower() in ["the", "a", "an", "that", "i", "you"]:
			return False
		else:
			return True
		
		
		
			
def get_photo_url(keyword, api_key):
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
			
def record_search(tweet_text, tweet_author, photo_url):
	'''Record the tweet data and the resulting image URL to the DB.'''
	Search.objects.create(tweet_text=tweet_text, tweet_author=tweet_author, image_url=photo_url)
		
def main_page(request):
	if fatal_error:
		objects = {'fatal_error': fatal_error}
	else:
		t = Tweet()
		try:
			photo_url = get_photo_url(t.keyword, api_key)
			flickr_result_found = True
		except NoHits:
			photo_url = None
			flickr_result_found = False
		if photo_url:
			record_search(t.text, t.author, photo_url)
			
		objects = {
			'tweet_text': t.text,
			'tweet_author': t.author,
			'query_word': t.keyword,
			'photo_url': photo_url,
			'flickr_result_found': flickr_result_found,
			'num_searches': Search.objects.count(),
			}
	return render_to_response('main-page.html', objects, context_instance=RequestContext(request))	

	