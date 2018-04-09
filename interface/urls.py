from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login_page'),
    path('index/', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout_view'),
    path('search/', views.search, name='search'),
]