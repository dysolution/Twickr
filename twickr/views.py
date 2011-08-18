import urllib2
			  
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

import logging
logger = logging.getLogger(__name__)

from getty.twickr.models import Search
from getty.twickr.objects import Word, Tweet
from getty.twickr.flickr import ApiKeyNotSet, NoHits, Photo

			
def main_page(request):
	t = Tweet()
	try:
		p = Photo(keyword=t.keyword)
		photo_url = p.url
	except ApiKeyNotSet:
		logger.critical('Please set the Flickr API key in settings.py.')
		return HttpResponse("The Flickr API key isn't set. Unable to search Flickr.")
	except NoHits:
		photo_url = None
		
	if photo_url:
		Search.objects.create(tweet_text=t.text, tweet_author=t.author, image_url=photo_url)
		
	objects = {
		'tweet_text': t.text,
		'tweet_author': t.author,
		'query_word': t.keyword,
		'photo_url': photo_url,
		'num_searches': Search.objects.count(),
		}
	return render_to_response('main-page.html', objects, context_instance=RequestContext(request))	

	