from django.contrib import admin
from interface.models import *

admin.site.register(twitteruser);
admin.site.register(tweet);
admin.site.register(retweet);
admin.site.register(favorite);
admin.site.register(follower);
