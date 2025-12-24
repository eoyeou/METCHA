from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
 
    genre_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return self.genre_name


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, help_text="TMDB 영화 ID")
    title = models.CharField(max_length=200, help_text="한국어 제목")
    original_title = models.CharField(max_length=200, blank=True, help_text="영어 원제")
    description = models.TextField(help_text="영어 설명 (AI embedding용)")
    kor_description = models.TextField(blank=True, help_text="한국어 설명 (UI 표시용)")
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
    heaviness = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="영화의 무게감 점수 (0-100)"
    )
    satisfaction = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="영화의 대중성 점수 (0-100)"
    )
    genres = models.ManyToManyField(Genre, through='MovieGenre', related_name='movies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movie'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['release_year']),
            models.Index(fields=['tmdb_id']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def update_rating(self):
        """영화의 평균 평점과 리뷰 수 업데이트"""
        from reviews.models import Review
        reviews = Review.objects.filter(movie=self)
        self.review_count = reviews.count()
        if self.review_count > 0:
            self.avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        else:
            self.avg_rating = 0.0
        self.save()


class MovieGenre(models.Model):
    """영화-장르 중간 테이블"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_genre'
        unique_together = ('movie', 'genre')

    def __str__(self):
        return f"{self.movie.title} - {self.genre.genre_name}"