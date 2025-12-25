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
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'is_following']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from accounts.models import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'content', 'is_spoiler', 
                  'likes_count', 'is_liked', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from reviews.models import ReviewLike
            return ReviewLike.objects.filter(
                user=request.user,
                review=obj
            ).exists()
        return False

''' 영화 목록용 - 간단한 정보 '''
class MovieListSerializer(serializers.ModelSerializer):

    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'description', 'kor_description', 'poster_url', 'release_year', 
                  'avg_rating', 'review_count', 'genres']

''' 영화 상세용 - 모든 정보 + 리뷰'''
class MovieDetailSerializer(serializers.ModelSerializer):

    genres = GenreSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'description', 'kor_description', 'poster_url',
                  'release_year', 'runtime', 'director', 'cast', 'avg_rating',
                  'review_count', 'genres', 'reviews', 'created_at']