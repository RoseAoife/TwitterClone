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
                    return render(request, 'Login.html', {'success': 'Account Created'} )
            else:
                return render(request, 'signup.html', {'error': 'Passwords Did\'t Match'})
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
        return render(request, 'login.html') 
        
def search(request):
    search_key = request.POST['search']
    user_list = [i['username'] for i in twitteruser.objects.filter(username__icontains=search_key).values('username')]
    return render(request, 'profile_search.html', {'user_list': user_list}) 
        
def profile(request):
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
    
    favorited = request.GET.get('favorite')
    retweeted = request.GET.get('retweet')
    
    if favorited:
        favorite.objects.create(tweetID_id=int(favorited), userID_id=request.user.username)
    if retweeted:
        retweet.objects.create(tweetID_id=int(retweeted), userID_id=request.user.username)
    
    if request.method == 'POST':
        if request.POST['follow'] == '1':
            follower.objects.create(userID_id=user_data, followerID_id=twitteruser.objects.get(username=request.user.username).username)
        if request.POST['follow'] == '2':
            follower.objects.get(userID_id=user_data, followerID_id=twitteruser.objects.get(username=request.user.username)).delete()
            
    followers = [ i['followerID_id'] for i in list(follower.objects.filter(userID_id=user_data).values('followerID_id'))]
    following = [ i['userID_id'] for i in list(follower.objects.filter(followerID_id=user_data).values('userID_id'))]
            
    if user_data not in [i['userID_id'] for i in list(follower.objects.filter(followerID_id=request.user.username).values('userID_id'))] and user_data != request.user.username:
        already_following = False
    elif user_data in [i['userID_id'] for i in list(follower.objects.filter(followerID_id=request.user.username).values('userID_id'))]:
        already_following = None
    else:
        already_following = True
        
    return render(request, 'profile.html', {'user_data': user_data, 'already_following': already_following, 'tweets': sorted_tweets, 'followers': followers, 'following': following, 'view': view, 'favorites': favorites, 'retweets': retweets}) 
    
def logout_view(request):
    logout(request)
    return render(request, 'login.html')
    
def settings(request):
    user_data = request.user.username
    
    if request.method == 'POST':
        if request.POST['setting'] == 'apply':
            username = request.POST['username']
            password = request.POST['password']
            if username:
                if username != request.user.username:
                    try:
                        user = User.objects.get(username=username)
                        return render(request, 'settings.html', {'error': 'Username Already Taken'} )
                    except User.DoesNotExist:
                        try:
                            user2 = twitteruser.objects.get(username=username)
                            return render(request, 'settings.html', {'error': 'Username Already Taken'} )
                        except twitteruser.DoesNotExist:
                            User.objects.get(username=user_data).username = username
                            twitteruser.objects.get(username=user_data).username = username
                            if password:
                                User.objects.get(username=username).set_password(password)
                                twitteruser.objects.get(username=username).password = password
                                
                        
            elif password:
                User.objects.get(username=user_data).set_password(password)
                twitteruser.objects.get(username=user_data).password = password
                
        elif request.POST['setting'] == 'delete':
            logout(request)
            twitteruser.objects.get(username=user_data).delete()
            User.objects.get(username=user_data).delete()
            return redirect(login_page)
            
    return render(request, 'settings.html')
