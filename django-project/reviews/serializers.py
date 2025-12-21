from rest_framework import serializers
from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['movie', 'rating', 'content', 'is_spoiler']
        
    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("평점은 0에서 5 사이여야 합니다.")
        return value


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'content', 'is_spoiler']