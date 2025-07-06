from django.contrib import admin
from django.urls import path,include

from . import views
app_name="myApp"
urlpatterns = [
    path('index/', views.IndexView.as_view(),name= 'index'),
    path('login/', views.login,name= 'login'),
    path('logout/', views.logout,name= 'logout'),
    path('register/', views.register,name= 'register'),
    path('realtime/', views.realtime,name= 'realtime'),
    path('predict/', views.predict,name= 'predict'),
    path('rank/', views.rank,name= 'rank'),
    path('year/', views.year,name= 'year'),
    path('gas/', views.gas,name= 'gas'),
    path('table/', views.table,name= 'table'),
    path('air/', views.air,name= 'air'),

   
]