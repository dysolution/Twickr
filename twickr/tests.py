from django.test import TestCase
from getty.twickr.views import Tweet, Word

class WordTest(TestCase):
	def setUp(self):
		self.good_words = ['foo','dollar','mix','cloud9','23skidoo']
		self.bad_words = ["the", "a", "an", "that", "I", "you"]

	def test_good_words(self):
		for word in self.good_words:
			self.assertTrue(Word(word).is_acceptable())
			
	def test_bad_words(self):
		for word in self.bad_words:
			self.assertFalse(Word(word).is_acceptable())

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

class AllowOddThirdWords(TestCase):
	def setUp(self):
		self.example_tweets = []
		self.example_tweets.append(Tweet(author='foo', text="Don't tell @mom the babysitter's dead."))
		self.example_tweets.append(Tweet(author='foo', text="This is solid."))
		self.example_tweets.append(Tweet(author='foo', text="I'm not leaving!!!!"))
		self.example_tweets.append(Tweet(author='foo', text="What is #trending now?"))

	def test_odd_third_words(self):
		self.assertEqual(self.example_tweets[0].keyword, "@mom")
		self.assertEqual(self.example_tweets[1].keyword, "solid.")
		self.assertEqual(self.example_tweets[2].keyword, "leaving!!!!")
		self.assertEqual(self.example_tweets[3].keyword, "#trending")

class PickCorrectWord(TestCase):
	def setUp(self):
		self.example_tweets = []
		self.example_tweets.append(Tweet(author='foo', text="I can't believe it's not butter."))
		self.example_tweets.append(Tweet(author='foo', text="You're not the boss of me."))
		self.example_tweets.append(Tweet(author='foo', text="I scream. You scream. Why are we screaming?"))
		
	def test_word_selection(self):
		self.assertEqual(self.example_tweets[0].keyword, "believe")
		self.assertEqual(self.example_tweets[1].keyword, "boss")
		self.assertEqual(self.example_tweets[2].keyword, "scream.")


