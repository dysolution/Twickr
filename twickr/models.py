from django.db import models

class Search(models.Model):

	tweet_text		= models.TextField(max_length=140)
	tweet_author	= models.CharField(max_length=256)
	image_url		= models.CharField(max_length=256)