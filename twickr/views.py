import urllib2
			  
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

import logging
logging.basicConfig(level=logging.INFO)

from getty.twickr.models import Search
from getty.twickr.objects import Word, Tweet, FailWhale
from getty.twickr.flickr import ApiKeyNotSet, NoHits, UnknownFlickrError, Photo

			
def main_page(request):
	t = Tweet()
	logging.info("Keyword: %s" % t.keyword)
	photo_url = None
	try:
		p = Photo(keyword=t.keyword)
		if p.url:
			photo_url = p.url
			Search.objects.create(tweet_text=t.text, tweet_author=t.author, image_url=photo_url)
	except ApiKeyNotSet:		
		return HttpResponse("Bad Flickr API key. Unable to search Flickr.")
	except UnknownFlickrError:
		logging.error("Unknown error while querying Flickr.")
	except NoHits:
		logging.warning("No Flickr hits for keyword: %s" % t.keyword)
		
	
		
	objects = {
		'tweet_text': t.text,
		'tweet_author': t.author,
		'query_word': t.keyword,
		'photo_url': photo_url,
		'num_searches': Search.objects.count(),
		}
	return render_to_response('main-page.html', objects, context_instance=RequestContext(request))	

	