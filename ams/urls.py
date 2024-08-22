"""
URL configuration for ams project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from base.views import login_view,logout_view,artist_create_view,register_view,dashboard_view,user_create_view,user_edit_view,user_delete_view,artist_edit_view,artist_delete_view,artist_music_view,artist_music_create_view,artist_music_edit_view,artist_music_delete_view,artist_csv_import,artist_csv_export

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('register/',register_view, name='register'),
    path('user-create/',user_create_view, name='user-create'),
    path('artist-create/',artist_create_view, name='artist-create'),
    path('user-edit/<int:pk>/',user_edit_view, name='user-edit'),
    path('artist-edit/<int:pk>/',artist_edit_view, name='artist-edit'),
    path('user-delete/<int:pk>/',user_delete_view, name='user-delete'),
    path('artist-delete/<int:pk>/',artist_delete_view, name='artist-delete'),
    path('artist-music/<int:pk>/',artist_music_view, name='artist-music'),
    path('artist-music-create/<int:pk>/',artist_music_create_view, name='artist-music-create'),
    path('artist-music-edit/<int:pk>/',artist_music_edit_view, name='artist-music-edit'),
    path('artist-music-delete/<int:pk>/',artist_music_delete_view, name='artist-music-delete'),
    path('artist-csv-import/',artist_csv_import, name='artist-csv-import'),
    path('artist-csv-export/',artist_csv_export, name='artist-csv-export'),
]
