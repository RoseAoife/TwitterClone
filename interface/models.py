from django.db import models
from datetime import datetime 

class twitteruser(models.Model):
    userID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=45)
    LastName = models.CharField(max_length=45)
    
class tweet(models.Model):
    tweetID = models.AutoField(primary_key=True)
    posterID = models.ForeignKey(twitteruser, on_delete=models.CASCADE)
    Message = models.CharField(max_length=140)
    PostTime = models.DateTimeField(default=datetime.now, blank=True)
    
class retweet(models.Model):
    retweetID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(twitteruser, on_delete=models.CASCADE)
    tweetID = models.ForeignKey(tweet, on_delete=models.CASCADE)
    
class favorite(models.Model):
    favoriteID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(twitteruser, on_delete=models.CASCADE)
    tweetID = models.ForeignKey(tweet, on_delete=models.CASCADE)
    
class follower(models.Model):
    class Meta:
        unique_together = (('userID', 'followerID'),)

    userID = models.ForeignKey(twitteruser, related_name="user_name", on_delete=models.CASCADE)
    followerID = models.ForeignKey(twitteruser, related_name="follower_name", on_delete=models.CASCADE)