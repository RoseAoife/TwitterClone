from django.shortcuts import render
from django.http import HttpResponse
import datetime
from interface.models import twitteruser
from interface.models import tweet
from interface.models import follower
from interface.models import favorite
from interface.models import retweet
from django.contrib.auth.models import User
from django.contrib.auth import logout , authenticate, login
from django.shortcuts import redirect

def login_page(request):
    if request.user.is_authenticated:
        return redirect(index)
        
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(index)
            else:
                error = "Username/Password Incorrect"
                return render(request, 'login.html', {'error': error})
        else:
            return render(request, 'login.html')
        
def signup(request):    
    if request.method == 'POST':
        if request.POST['password'] == '' or request.POST['password2'] == '' or request.POST['username'] == '':
            return render(request, 'signup.html', {'error': 'Leave no fields empty'} )
        else:
            if request.POST['password'] == request.POST['password2']:
                try:
                    User.objects.get(username=request.POST['username'])
                    return render(request, 'signup.html', {'error': 'Username Already Taken'} )
                except User.DoesNotExist:
                    User.objects.create_user(request.POST['username'], password=request.POST['password'])
                    twitteruser.objects.create(username=request.POST['username'], password=request.POST['password'])
                    return render(request, 'login.html', {'success': 'Account Created'} )
            else:
                return render(request, 'signup.html', {'error': 'Passwords Didn\'t Match'})
    else:
        return render(request, 'signup.html')
        
def index(request):
    if request.user.is_authenticated:   
        following = [i['userID_id'] for i in list(follower.objects.filter(followerID_id=request.user.username).values('userID_id'))]
        following.append(request.user.username)
        favorites = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        retweets = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        current_user = twitteruser.objects.get(username=request.user.username)
        
        favorited = request.GET.get('favorite')
        retweeted = request.GET.get('retweet')
        deleted = request.GET.get('deleted')

        if favorited:
            if int(favorited) not in favorites:
                favorite.objects.create(tweetID_id=int(favorited), userID_id=current_user.username)
            else:
                favorite.objects.get(tweetID_id=int(favorited), userID_id=current_user.username).delete()
            return redirect(index)
        if retweeted:
            if int(retweeted) not in retweets:
                retweet.objects.create(tweetID_id=int(retweeted), userID_id=current_user.username)
            else:
                retweet.objects.get(tweetID_id=int(retweeted), userID_id=current_user.username).delete()
            return redirect(index)
        if deleted:
            tweet.objects.get(tweetID=int(deleted), posterID_id=current_user.username).delete()
            return redirect(index)
            
        view = request.GET.get('view')
        if view == 'favorites':
            tweets = list(tweet.objects.filter(tweetID__in=favorites).values())
        elif view == 'retweets':
            tweets = list(tweet.objects.filter(tweetID__in=retweets).values())
        else:
            tweets = list(tweet.objects.filter(posterID_id__in=following).values())
            rtweets = list(tweet.objects.filter(tweetID__in=retweets).values())
            for i in rtweets:
                if not any(j['tweetID'] == i['tweetID'] for j in tweets):
                    tweets.append(i.copy())

        sorted_tweets = [(dict_['PostTime'], dict_) for dict_ in tweets]
        sorted_tweets.sort(reverse=True)
        sorted_tweets = [dict_ for (key, dict_) in sorted_tweets]
        
        if request.method == 'POST':
            if request.POST['message'] == "":
                return redirect(index)
            tweet.objects.create(posterID_id=current_user.username, Message=request.POST['message'], PostTime=datetime.datetime.now())
            return redirect(index)
            
        else:
            return render(request, 'index.html', {'tweets': sorted_tweets, 'view': view, 'favorites': favorites, 'retweets': retweets})
    else:
        return redirect(login_page) 
        
def search(request):  
    if request.user.is_authenticated:

        try:
            search_key = request.POST['search']
        except:
            search_key = request.GET.get('search_key')
            if search_key is None:
                search_key = ''
    
        favorited = request.GET.get('favorite')
        retweeted = request.GET.get('retweet')
        deleted = request.GET.get('deleted')
        
        self_favs = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        self_ret = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        
        if favorited:
            if int(favorited) not in self_favs:
                favorite.objects.create(tweetID_id=int(favorited), userID_id=request.user.username)
            else:
                favorite.objects.get(tweetID_id=int(favorited), userID_id=request.user.username).delete()
        if retweeted:
            if int(retweeted) not in self_ret:
                retweet.objects.create(tweetID_id=int(retweeted), userID_id=request.user.username)
            else:
                retweet.objects.get(tweetID_id=int(retweeted), userID_id=request.user.username).delete()
        if deleted:
            try:
                tweet.objects.get(tweetID=int(deleted), posterID_id=request.user.username).delete()
            except:
                pass
            
        self_favs = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        self_ret = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
            
        favorites = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        retweets = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
            
        user_list = [i['username'] for i in twitteruser.objects.filter(username__icontains=search_key).values('username')]
        tweets = [i for i in tweet.objects.filter(Message__icontains=search_key).values()]
        
        sorted_tweets = [(dict_['PostTime'], dict_) for dict_ in tweets]
        sorted_tweets.sort(reverse=True)
        sorted_tweets = [dict_ for (key, dict_) in sorted_tweets]
        
        return render(request, 'search.html', {'data': request.POST, 'user_list': user_list, 'tweets': sorted_tweets, 'retweets': retweets, 'favorites': favorites, 'search_key': search_key}) 
        
    else:
        return redirect(login)
        
def profile(request):
    if request.user.is_authenticated:

        favorited = request.GET.get('favorite')
        retweeted = request.GET.get('retweet')
        deleted = request.GET.get('deleted')
        
        self_favs = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        self_ret = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        
        if favorited:
            if int(favorited) not in self_favs:
                favorite.objects.create(tweetID_id=int(favorited), userID_id=request.user.username)
            else:
                favorite.objects.get(tweetID_id=int(favorited), userID_id=request.user.username).delete()
        if retweeted:
            if int(retweeted) not in self_ret:
                retweet.objects.create(tweetID_id=int(retweeted), userID_id=request.user.username)
            else:
                retweet.objects.get(tweetID_id=int(retweeted), userID_id=request.user.username).delete()
        if deleted:
            try:
                tweet.objects.get(tweetID=int(deleted), posterID_id=request.user.username).delete()
            except:
                pass
            
        self_favs = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=request.user.username).values('tweetID_id'))]
        self_ret = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=request.user.username).values('tweetID_id'))]

        user_data = request.GET.get('user')

        favorites = [i['tweetID_id'] for i in list(favorite.objects.filter(userID_id=user_data).values('tweetID_id'))]
        retweets = [i['tweetID_id'] for i in list(retweet.objects.filter(userID_id=user_data).values('tweetID_id'))]
        
        view = request.GET.get('view')
        if view == 'favorites':
            tweets = list(tweet.objects.filter(tweetID__in=favorites).values())
        elif view == 'retweets':
            tweets = list(tweet.objects.filter(tweetID__in=retweets).values())
        else:
            tweets = tweet.objects.filter(posterID_id=user_data).values()
        
        sorted_tweets = [(dict_['PostTime'], dict_) for dict_ in tweets]
        sorted_tweets.sort(reverse=True)
        sorted_tweets = [dict_ for (key, dict_) in sorted_tweets]
        
        if request.method == 'POST':
            try:
                if request.POST['follow'] == '1':
                    follower.objects.create(userID_id=user_data, followerID_id=twitteruser.objects.get(username=request.user.username).username)
                if request.POST['follow'] == '2':
                    follower.objects.get(userID_id=user_data, followerID_id=twitteruser.objects.get(username=request.user.username)).delete()
            except:
                pass
                
        followers = [ i['followerID_id'] for i in list(follower.objects.filter(userID_id=user_data).values('followerID_id'))]
        following = [ i['userID_id'] for i in list(follower.objects.filter(followerID_id=user_data).values('userID_id'))]
                
        if user_data not in [i['userID_id'] for i in list(follower.objects.filter(followerID_id=request.user.username).values('userID_id'))] and user_data != request.user.username:
            already_following = False
        elif user_data in [i['userID_id'] for i in list(follower.objects.filter(followerID_id=request.user.username).values('userID_id'))]:
            already_following = None
        else:
            already_following = True
          
        try:
            data = request.POST['user']
        except:
            data = 'No Post Data'
            
        return render(request, 'profile.html', {'data': data, 'user_data': user_data, 'already_following': already_following, 'tweets': sorted_tweets, 'followers': followers, 'following': following, 'view': view, 'favorites': favorites, 'retweets': retweets, 'self_favs': self_favs, 'self_ret': self_ret}) 
    
    else:
        return redirect(login)
  
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'login.html')
        
    else:
        return redirect(login)
    
def settings(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
        
            username = request.user.username
            
            if request.POST['setting'] == 'apply':
            
                password = request.POST['password']
                
                if password:
                    current_user = User.objects.get(username=request.user.username)
                    current_twittertwitteruser = twitteruser.objects.get(username=request.user.username)
                    
                    current_user.set_password(password)
                    current_twittertwitteruser.Password = password
                    
                    current_user.save()
                    current_twittertwitteruser.save()
                    
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect(settings)
                    else:
                        error = "Username/Password Incorrect"
                        return render(request, 'login.html', {'error': error})
                                
                return redirect(settings)

            elif request.POST['setting'] == 'delete':
                logout(request)
                twitteruser.objects.get(username=username).delete()
                User.objects.get(username=username).delete()
                return redirect(login_page)
            
        return render(request, 'settings.html')
    
    else:

        return redirect(login)
    
def handler404(request):
    return render(request.build_absolute_uri().rsplit('/', 1)[0] + '/')


def handler500(request):
    return render(request.build_absolute_uri().rsplit('/', 1)[0] + '/')