from django.urls import path
from . import views
from . import search_views

app_name = 'movies'

urlpatterns = [
    path('movies/', views.movie_list),
    path('movies/<int:movie_pk>/', views.movie_detail),
    path('movies/<int:movie_pk>/similar/', views.similar_movies),
    path('movies/search/semantic/', search_views.semantic_search),
]