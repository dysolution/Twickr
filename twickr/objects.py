import logging
import urllib2
			  
from django.utils import simplejson
from django.utils.encoding import smart_unicode

logger = logging.getLogger(__name__)

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


