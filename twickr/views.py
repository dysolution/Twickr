import urllib2
			  
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

fatal_error = None

import logging
logger = logging.getLogger(__name__)

from getty.twickr.models import Search
from getty.twickr.objects import Word, Tweet
from getty.twickr.flickr import NoHits, get_photo_url

			
def main_page(request):
	if fatal_error:
		objects = {'fatal_error': fatal_error}
	else:
		t = Tweet()
		try:
			photo_url = get_photo_url(t.keyword)
			if photo_url:
				Search.objects.create(tweet_text=t.text, tweet_author=t.author, image_url=photo_url)
		except NoHits:
			photo_url = None
			
		objects = {
			'tweet_text': t.text,
			'tweet_author': t.author,
			'query_word': t.keyword,
			'photo_url': photo_url,
			'num_searches': Search.objects.count(),
			}
	return render_to_response('main-page.html', objects, context_instance=RequestContext(request))	

	