from django.contrib import admin
from django.urls import path,include

from . import views
urlpatterns = [
    path('index/', views.index,name= 'index'),
    path('login/', views.login,name= 'login'),
    path('logout/', views.logout,name= 'logout'),
    path('register/', views.register,name= 'register'),
    path('realtime/', views.realtime,name= 'realtime'),
    path('predict/', views.predict,name= 'predict'),
    path('rank/', views.rank,name= 'rank'),
    path('dist/', views.dist,name= 'dist'),
    path('monthly/', views.monthly,name= 'monthly'),
    path('year/', views.year,name= 'year'),
    
]