from getty.twickr.models import Search
from django.contrib import admin

class SearchAdmin(admin.ModelAdmin):
	list_display = ['tweet_author','tweet_text','image_url',]
	#ordering = ['faved_by']
	search_fields = ['tweet_text','tweet_author']
	
admin.site.register(Search, SearchAdmin)