from django.shortcuts import render
from django.http import HttpResponse
import datetime
from interface.models import twitteruser

def index(request):
    if request.method == 'POST':
        data = 'user not found'
        username = request.POST['username']
        password = request.POST['password']
        
        user = twitteruser.objects.filter(username=username)
        
        if user:
            data = 'user found'
        
        return render(request, 'login.html', {'data': data})
    else:
        return render(request, 'login.html')
    
