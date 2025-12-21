from rest_framework import serializers
from .models import Review
from movies.models import Movie


class ReviewCreateSerializer(serializers.ModelSerializer):
    """리뷰 작성용"""
    class Meta:
        model = Review
        fields = ['movie', 'rating', 'content', 'is_spoiler']
        
    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("평점은 0에서 5 사이여야 합니다.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """리뷰 수정용"""
    class Meta:
        model = Review
        fields = ['rating', 'content', 'is_spoiler']