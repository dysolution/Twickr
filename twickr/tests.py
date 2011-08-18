from django.test import TestCase
from getty.twickr.views import Tweet, Word

class WordTest(TestCase):
	def setUp(self):
		self.good_words = ['foo','dollar','mix','cloud9','23skidoo']
		self.bad_words = ["the", "a", "an", "that", "I", "you"]

	def test_good_words(self):
		for word in self.good_words:
			self.assertEqual(Word(word).is_acceptable(), True)
			
	def test_bad_words(self):
		for word in self.bad_words:
			self.assertEqual(Word(word).is_acceptable(), False)
			
class TweetTooShort(TestCase):
	def setUp(self):
		self.tweet = Tweet(author='dysolution', text='Too short.')

	def test_tweet_length(self):
		self.assertEqual(self.tweet.keyword, None)
			
class NoValidKeywords(TestCase):
	def setUp(self):
		self.tweet = Tweet(author='dysolution', text="I'll give you the")

	def test_tweet_length(self):
		self.assertEqual(self.tweet.keyword, None)
		
class PickCorrectWord(TestCase):
	def setUp(self):
		self.tweet = Tweet(author='dysolution', text="I can't believe it's not butter.")

	def get_third_word(self):
		self.assertEqual(self.tweet.keyword, "believe")
