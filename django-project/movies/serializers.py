from rest_framework import serializers
from .models import Movie, Genre
from reviews.models import Review

# User 모델 import 추가
from accounts.models import User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'genre_name']


class ReviewUserSerializer(serializers.ModelSerializer):
    """리뷰 작성자 정보"""
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'content', 'is_spoiler', 
                  'likes_count', 'created_at', 'updated_at']


class MovieListSerializer(serializers.ModelSerializer):
    """영화 목록용 - 간단한 정보"""
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'release_year', 
                  'avg_rating', 'review_count', 'genres']


class MovieDetailSerializer(serializers.ModelSerializer):
    """영화 상세용 - 모든 정보 + 리뷰"""
    genres = GenreSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'description', 'poster_url',
                  'release_year', 'runtime', 'director', 'cast', 'avg_rating',
                  'review_count', 'genres', 'reviews', 'created_at']