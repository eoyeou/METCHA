from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User, PreferenceReport, Follow
from reviews.models import Review


class UserSimpleSerializer(serializers.ModelSerializer):
    """사용자 간단 정보 Serializer (목록용)"""
    review_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'profile_image', 'review_count', 'is_following'
        ]
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 정보 Serializer"""
    review_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile_image', 'review_count', 'followers_count', 'following_count',
            'is_following', 'is_self'
        ]
    
    def get_profile_image(self, obj):
        """프로필 이미지 전체 URL 반환"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False
    
    def get_is_self(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.id == obj.id
        return False


class UserReviewSerializer(serializers.ModelSerializer):
    """사용자 리뷰 목록 Serializer"""
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.URLField(source='movie.poster_url', read_only=True)
    movie_id = serializers.IntegerField(source='movie.id', read_only=True)
    movie_heaviness = serializers.IntegerField(source='movie.heaviness', read_only=True, allow_null=True)
    movie_satisfaction = serializers.IntegerField(source='movie.satisfaction', read_only=True, allow_null=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'movie_id', 'movie_title', 'movie_poster',
            'movie_heaviness', 'movie_satisfaction',
            'rating', 'content', 'is_spoiler', 'likes_count',
            'created_at', 'updated_at'
        ]


class PreferenceReportSerializer(serializers.ModelSerializer):
    """취향 리포트 Serializer"""
    
    class Meta:
        model = PreferenceReport
        fields = [
            'id', 'genre_distribution', 'mood_analysis',
            'director_preferences', 'top_rated_movies', 'summary',
            'generated_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        # Token 생성
        Token.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
            if not user.is_active:
                raise serializers.ValidationError("비활성화된 계정입니다.")
            data['user'] = user
        else:
            raise serializers.ValidationError("아이디와 비밀번호를 입력해주세요.")
        
        return data

