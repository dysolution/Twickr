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