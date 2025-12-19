from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from pgvector.django import VectorField


class User(AbstractUser):

    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username


class Genre(models.Model):
    genre_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return self.genre_name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    poster_url = models.URLField(max_length=500, blank=True)
    release_year = models.IntegerField()
    runtime = models.IntegerField(help_text="상영 시간 (분)")
    director = models.CharField(max_length=100)
    cast = models.TextField(help_text="출연진 (쉼표로 구분)")
    avg_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    review_count = models.IntegerField(default=0)
    genres = models.ManyToManyField(Genre, through='MovieGenre', related_name='movies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movie'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['release_year']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class MovieGenre(models.Model):
    """영화-장르 중간 테이블"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_genre'
        unique_together = ('movie', 'genre')

    def __str__(self):
        return f"{self.movie.title} - {self.genre.genre_name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
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
        unique_together = ('user', 'movie')  # 한 사용자가 한 영화에 하나의 리뷰만
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}★)"


class ReviewEmbedding(models.Model):
    """리뷰 임베딩 모델 (RAG용)"""
    review = models.OneToOneField(
        Review, 
        on_delete=models.CASCADE, 
        related_name='embedding'
    )
    # pgvector 사용 시 (PostgreSQL + pgvector 확장 필요)
    embedding_vector = VectorField(dimensions=1536)  # OpenAI embedding 차원
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_embedding'

    def __str__(self):
        return f"Embedding for Review #{self.review.id}"


class Watchlist(models.Model):
    STATUS_CHOICES = [
        ('want', '보고싶어요'),
        ('watching', '보는중'),
        ('watched', '봤어요'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlist')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='want')
    watched_at = models.DateTimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.get_status_display()})"


class PreferenceReport(models.Model):
 
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='preference_reports'
    )
    genre_distribution = models.JSONField(
        help_text="장르별 선호도 분포 {'액션': 30, '드라마': 50, ...}"
    )
    mood_analysis = models.JSONField(
        help_text="무드 분석 결과 {'우울한': 20, '유쾌한': 40, ...}"
    )
    director_preferences = models.JSONField(
        help_text="선호 감독 {'봉준호': 5, '크리스토퍼 놀란': 3, ...}"
    )
    top_rated_movies = models.JSONField(
        help_text="높은 평점을 준 영화 리스트"
    )
    summary = models.TextField(help_text="취향 분석 요약")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'preference_report'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', '-generated_at']),
        ]

    def __str__(self):
        return f"{self.user.username}의 취향 리포트 ({self.generated_at.date()})"