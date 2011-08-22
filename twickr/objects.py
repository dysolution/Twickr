import logging
import urllib2
import re
			  
from django.utils import simplejson
from django.utils.encoding import smart_unicode

#logger = logging.getLogger(__name__)

class Word():
	def __init__(self, content):
		self.content = content
		
	def is_acceptable(self):
		'''Defines criteria under which a word will be acceptable
		as a keyword with which to search Flickr.
		
		Sanitize the word before it's used as a query on Flickr
		by adding additional elif statements here if desired.'''
		
		# Allow @usernames and words with trailing punctuation.
		if re.match("^@?[\w']+[.!?:]*$", self.content) is None:
			return False
			
		if self.content.lower() in ["the", "a", "an", "that", "i", "you"]:
			return False
		else:
			return True
			
class FailWhale(Exception):
	pass

class TwitterError(Exception):
	pass
	
class BadTwitterResponse(Exception):
	pass
	
class Tweet():

	def __init__(self, author=None, text=None, response_from_twitter=None):
		'''Query Twitter for a tweet and parse the response to 
		extract its author and its text.
		
		For testing purposes, a tweet or error condition can be simulated:
		
		1. just an author and some text
		2. JSON or HTML (for some errors) in the same format that Twitter returns
		'''
		self.author = author
		self.text = text
		self.response_from_twitter = response_from_twitter
		
		if self.author and self.text:
			logging.info("Testing with manufactured tweet: @%s: %s" %
			(self.author, self.text))
			self.get_words()
			self.get_keyword()
		elif self.response_from_twitter:
			logging.info("Testing with simulated Twitter response.")
			self.parse_twitter_response()
			self.get_words()
			self.get_keyword()
		else:
			self.query_twitter()
			try:
				self.parse_twitter_response()
			except:
				self.words = None
				self.keyword = None
				raise BadTwitterResponse
			
			self.author = self.tweet_dict['user']['screen_name']
			self.text = self.tweet_dict['text']
			logging.debug("Tweet text: %s" % self.text)
			self.get_words()
			self.get_keyword()
				
			
		
	def query_twitter(self):
		'''Query the Twitter public timeline without
		passing OAuth credentials to get a JSON response.'''
		query_url='http://api.twitter.com/1/statuses/public_timeline.json?count=1'
		logging.debug("Twitter query URL: %s" % query_url)
		request = urllib2.Request(query_url)
		try:
			self.response_from_twitter = urllib2.urlopen(request)
		except urllib2.URLError, msg:
			logging.error("Couldn't contact Twitter: %s" % msg)
			self.response_from_twitter = None
			
	def parse_twitter_response(self):
		'''Try to parse Twitter's response into JSON, then extract from
		the JSON a dict with the tweet properties as keys.'''
		try:
			self.parsed_json = simplejson.load(self.response_from_twitter)
			self.tweet_dict = self.parsed_json[0]	
		except:
			if "<title>" in self.response_from_twitter:
				'''HTML response instead of JSON. There was an error
				like a "fail whale."'''
				self.tweet_dict = None
				if "over capacity" in self.response_from_twitter.lower():
					raise FailWhale
				else:
					raise TwitterError
			raise
			
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
				logging.warning('No acceptable keyword found in tweet. Words: %s' % self.words)
				self.keyword = None


