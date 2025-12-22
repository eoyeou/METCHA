from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Movie
from .serializers import MovieDetailSerializer, MovieListSerializer


@api_view(['GET'])
def movie_list(request):
    """영화 목록 조회 (필터링 지원)"""
    movies = Movie.objects.all().prefetch_related('genres')
    
    # 쿼리 파라미터로 필터링
    genre = request.GET.get('genre')
    order_by = request.GET.get('order_by', '-created_at')  # 기본값: 최신순
    
    if genre:
        # 장르별 필터링 (대소문자 구분 없이)
        # 한국어/영어 모두 지원
        genre_mapping = {
            '드라마': ['드라마', 'Drama', 'drama'],
            '액션': ['액션', 'Action', 'action'],
            '공포': ['공포', 'Horror', 'horror'],
            '코미디': ['코미디', 'Comedy', 'comedy'],
            'Drama': ['드라마', 'Drama', 'drama'],
            'Action': ['액션', 'Action', 'action'],
            'Horror': ['공포', 'Horror', 'horror'],
            'Comedy': ['코미디', 'Comedy', 'comedy'],
        }
        
        # 매핑된 장르 이름들로 검색
        search_terms = genre_mapping.get(genre, [genre])
        from django.db.models import Q
        query = Q()
        for term in search_terms:
            query |= Q(genres__genre_name__icontains=term)
        movies = movies.filter(query).distinct()
    
    # 정렬
    if order_by == 'rating':
        movies = movies.order_by('-avg_rating', '-review_count')
    elif order_by == 'reviews':
        movies = movies.order_by('-review_count', '-avg_rating')
    else:
        movies = movies.order_by('-created_at')
    
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(
        Movie.objects.prefetch_related('genres', 'reviews__user'), 
        pk=movie_pk
    )
    serializer = MovieDetailSerializer(movie, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def similar_movies(request, movie_pk):
    """비슷한 영화 추천 (같은 장르 기반)"""
    movie = get_object_or_404(Movie.objects.prefetch_related('genres'), pk=movie_pk)
    
    # 현재 영화의 장르 가져오기
    movie_genres = movie.genres.all()
    
    if not movie_genres.exists():
        # 장르가 없으면 최신 영화 중에서 추천
        similar = Movie.objects.exclude(pk=movie_pk).order_by('-created_at')[:12]
    else:
        # 같은 장르를 가진 영화 찾기 (최소 1개 이상의 공통 장르)
        genre_ids = [genre.id for genre in movie_genres]
        similar = Movie.objects.filter(
            genres__id__in=genre_ids
        ).exclude(
            pk=movie_pk
        ).distinct().order_by('-avg_rating', '-created_at')[:12]
        
        # 같은 장르 영화가 12개 미만이면 최신 영화로 채우기
        if similar.count() < 12:
            additional = Movie.objects.exclude(
                pk__in=[m.id for m in similar] + [movie.id]
            ).order_by('-created_at')[:12 - similar.count()]
            similar = list(similar) + list(additional)
    
    serializer = MovieListSerializer(similar, many=True)
    return Response(serializer.data)