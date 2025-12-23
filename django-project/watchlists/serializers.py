from rest_framework import serializers
from .models import Watchlist
from movies.serializers import MovieListSerializer


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'movie_id', 'status', 'added_at', 'watched_at']
        read_only_fields = ['id', 'added_at', 'watched_at']

