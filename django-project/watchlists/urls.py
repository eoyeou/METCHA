# watchlists/urls.py
from django.urls import path
from . import views

app_name = 'watchlists'

urlpatterns = [
    path('watchlists/', views.watchlist_list),
    path('watchlists/<int:movie_id>/', views.watchlist_delete),
    path('watchlists/<int:movie_id>/check/', views.watchlist_check),
]