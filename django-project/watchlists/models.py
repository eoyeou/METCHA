from django.db import models
from django.conf import settings

from movies.models import Movie


class Watchlist(models.Model):
    """
    위시리스트 모델
    사용자가 보고싶은 영화를 저장하는 기능
    현재는 'want' 상태만 사용 (위시리스트)
    """
    STATUS_CHOICES = [
        ('want', '보고싶어요'),  # 위시리스트 (현재 사용 중)
        ('watching', '보는중'),  # 미사용 (향후 확장 가능)
        ('watched', '봤어요'),  # 미사용 (리뷰와 중복)
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='watchlist'
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlist')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='want')
    watched_at = models.DateTimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-watched_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.get_status_display()})"
