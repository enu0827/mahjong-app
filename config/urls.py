"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from mahjong.views import home, add_game, game_list,season_ranking,player_detail
from mahjong.views import home, add_game, game_list, season_ranking, player_detail, daily_summary

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('add/', add_game, name='add_game'),
    path('games/', game_list, name='game_list'),
    path('ranking/', season_ranking, name='season_ranking'),
    path('player/<int:player_id>/', player_detail, name='player_detail'),
    path('daily/', daily_summary, name='daily_summary'),
]