from django.contrib import admin
from django.urls import path,include
from app import views
from django.contrib.auth import views as auth_views


urlpatterns = [
  path('',views.index,name='index'),
  path('contact',views.contact,name='contact'),
  path('weather',views.weather,name='weather'),
  path('signUp',views.signUp,name='signUp'),
  path('login',views.handlelogin,name='handlelogin'),
  path('logout',views.handlelogout,name='handlelogout'),
  path('search',views.search,name='search'),
]