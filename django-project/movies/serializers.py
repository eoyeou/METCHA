from rest_framework import serializers
from .models import Movie, Genre
from reviews.models import Review

from accounts.models import User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'genre_name']


'''리뷰 작성자 정보'''
class ReviewUserSerializer(serializers.ModelSerializer):
                                                                
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'content', 'is_spoiler', 
                  'likes_count', 'created_at', 'updated_at']

''' 영화 목록용 - 간단한 정보 '''
class MovieListSerializer(serializers.ModelSerializer):

    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'release_year', 
                  'avg_rating', 'review_count', 'genres']

''' 영화 상세용 - 모든 정보 + 리뷰'''
class MovieDetailSerializer(serializers.ModelSerializer):

    genres = GenreSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'description', 'poster_url',
                  'release_year', 'runtime', 'director', 'cast', 'avg_rating',
                  'review_count', 'genres', 'reviews', 'created_at']