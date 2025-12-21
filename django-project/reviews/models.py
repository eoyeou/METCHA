from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from movies.models import Movie


class Review(models.Model):
    """리뷰 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    content = models.TextField()
    likes_count = models.IntegerField(default=0)
    is_spoiler = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review'
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}★)"

    def save(self, *args, **kwargs):
        """리뷰 저장 후 영화 평점 업데이트"""
        super().save(*args, **kwargs)
        self.movie.update_rating()


class ReviewEmbedding(models.Model):
    """리뷰 임베딩 모델 (추천 시스템용)"""
    review = models.OneToOneField(
        Review, 
        on_delete=models.CASCADE, 
        related_name='embedding'
    )
    # 임베딩 벡터를 JSONField로 저장 (배열 형태)
    embedding_vector = models.JSONField(
        help_text="리뷰 텍스트 임베딩 벡터 (배열 형태)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_embedding'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Embedding for Review #{self.review.id}"