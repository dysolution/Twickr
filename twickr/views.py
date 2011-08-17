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
	
def get_latest_public_tweet():
	'''Query the Twitter public timeline without
	passing OAuth credentials, parse the result
	as JSON, and return the data, which is indexed by
	tweet properties as keys.'''
	request = urllib2.Request('http://api.twitter.com/1/statuses/public_timeline.json?count=1')
	try:
		response = urllib2.urlopen(request)
	except urllib2.URLError, msg:
		logger.error("Couldn't contact Twitter: %s" % msg)
		return None
	try:	
		return simplejson.load(response)[0]	
	except Exception, msg:
		logger.error("Couldn't parse JSON: %s: %s" % (Exception, msg))
		return None
		
def word_is_acceptable(word):
	'''Defines criteria under which a word will be acceptable
	as a keyword with which to search Flickr.
	
	Sanitize the word before it's used as a query on Flickr
	by adding additional elif statements here if desired.'''
	try:
		# We only want simple ASCII keywords.
		word.encode('ascii')
	except UnicodeEncodeError:
		return False
		
	if word.lower() in ["the", "a", "an", "that", "i", "you"]:
		return False
	else:
		return True
		
def parse_tweet(tweet_json):
	'''Return the text and author of the tweet if the data is acceptable.'''
	# Sanitize the data here if desired.
	if tweet_json is None:
		return None, None
	else:
		return tweet_json['text'], tweet_json['user']['screen_name']
	
def get_words_from_tweet(tweet_text):
	'''Words are defined as the tokens created when the tweet is
	split on whitespace.'''
	if tweet_text:
		words = tweet_text.split()
		# Sanitize the words further here if desired.
		return words
	else:
		return None
	
def get_word_for_flickr_query(words):
	'''Given a list of the words in a tweet, return the desired
	keyword, or None if nothing acceptable can be found.
	
	Criterion: Either the third word or the next acceptable word
	given the list of exclusions.'''	
	if not words:
		logging.warning('No words provided to get_word_for_flickr_query.')
		return None
	else:
		if len(words) < 3:
			logging.warning('Not enough words in phrase. Words: %s' % words)
			return None
			
		'''Starting with the 3rd word in the tweet,
		look for the first acceptable word.'''
		acceptable_word = None
		for x in range(2, len(words)):
			if word_is_acceptable(words[x]):
				acceptable_word = words[x]					
				break
		if acceptable_word:
			return acceptable_word		
		else:
			logging.warning('No acceptable words found in tweet.')
			return None
			
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
		tweet = get_latest_public_tweet()
		tweet_text, tweet_author = parse_tweet(tweet)		
		words = get_words_from_tweet(tweet_text)
		flickr_query_word = get_word_for_flickr_query(words)		
		try:
			photo_url = get_photo_url(flickr_query_word, api_key)
			flickr_result_found = True
		except NoHits:
			photo_url = None
			flickr_result_found = False
		if photo_url:
			record_search(tweet_text, tweet_author, photo_url)
			
		objects = {
			'tweet_text': tweet_text,
			'tweet_author': tweet_author,
			'query_word': flickr_query_word,
			'photo_url': photo_url,
			'flickr_result_found': flickr_result_found,
			'num_searches': Search.objects.count(),
			}
	return render_to_response('main-page.html', objects, context_instance=RequestContext(request))	

	