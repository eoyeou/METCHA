# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 사용자 취향 점수 (4~5점 준 영화들의 평균)
    avg_heaviness = models.FloatField(
        null=True,
        blank=True,
        help_text="사용자 평균 Heaviness 점수 (0-100)"
    )
    avg_satisfaction = models.FloatField(
        null=True,
        blank=True,
        help_text="사용자 평균 Satisfaction 점수 (0-100)"
    )

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username
    
    def update_preference_scores(self):
        """사용자가 4~5점 준 영화들의 평균 Heaviness, Satisfaction 계산"""
        from reviews.models import Review
        from movies.models import Movie
        
        # 4점 이상 평점을 준 리뷰들
        high_rated_reviews = Review.objects.filter(
            user=self,
            rating__gte=4.0
        ).select_related('movie')
        
        # 해당 영화들의 Heaviness, Satisfaction 수집
        heaviness_scores = []
        satisfaction_scores = []
        
        for review in high_rated_reviews:
            movie = review.movie
            if movie.heaviness is not None:
                heaviness_scores.append(movie.heaviness)
            if movie.satisfaction is not None:
                satisfaction_scores.append(movie.satisfaction)
        
        # 평균 계산
        if heaviness_scores:
            self.avg_heaviness = sum(heaviness_scores) / len(heaviness_scores)
        else:
            self.avg_heaviness = None
            
        if satisfaction_scores:
            self.avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
        else:
            self.avg_satisfaction = None
        
        self.save(update_fields=['avg_heaviness', 'avg_satisfaction'])
        return self.avg_heaviness, self.avg_satisfaction


class Follow(models.Model):
    """사용자 팔로우 관계 모델"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text="팔로우를 하는 사용자"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="팔로우를 받는 사용자"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follow'
        unique_together = ('follower', 'following')  # 중복 팔로우 방지
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def clean(self):
        """자기 자신을 팔로우하는 것 방지"""
        from django.core.exceptions import ValidationError
        if self.follower == self.following:
            raise ValidationError("자기 자신을 팔로우할 수 없습니다.")


class PreferenceReport(models.Model):
    """개인 취향 리포트 모델 (Profile Page용)"""
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