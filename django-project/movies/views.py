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
    # ManyToMany 관계이므로 prefetch_related 사용
    movies = Movie.objects.prefetch_related('genres').all()
    
    # 쿼리 파라미터로 필터링
    genre = request.GET.get('genre')
    order_by = request.GET.get('order_by', '-created_at')  # 기본값: 최신순
    
    if genre:
        # 장르별 필터링
        from django.db.models import Q
        from .models import Genre
        
        # DB에 있는 실제 장르 이름 확인
        all_genres = Genre.objects.values_list('genre_name', flat=True)
        print(f"[장르 필터링] 요청된 장르: {genre}")
        print(f"[장르 필터링] DB에 있는 장르 목록: {list(all_genres)}")
        
        # 장르 매핑 (한국어 <-> 영어)
        genre_mapping = {
            '드라마': ['드라마', 'Drama'],
            '액션': ['액션', 'Action'],
            '공포': ['공포', 'Horror'],
            '코미디': ['코미디', 'Comedy'],
            'Drama': ['드라마', 'Drama'],
            'Action': ['액션', 'Action'],
            'Horror': ['공포', 'Horror'],
            'Comedy': ['코미디', 'Comedy'],
        }
        
        # 매핑된 장르 이름들로 검색
        search_terms = genre_mapping.get(genre, [genre])
        
        # DB에 실제로 존재하는 장르 이름만 사용
        valid_terms = []
        for term in search_terms:
            # 정확히 일치하는 장르 찾기
            matching_genres = [g for g in all_genres if term.lower() in g.lower() or g.lower() in term.lower()]
            if matching_genres:
                valid_terms.extend(matching_genres)
        
        if not valid_terms:
            # 매핑이 없으면 원본 검색어 사용
            valid_terms = [genre]
        
        print(f"[장르 필터링] 검색할 장르 이름: {valid_terms}")
        
        # 장르 필터링
        query = Q()
        for term in valid_terms:
            query |= Q(genres__genre_name__iexact=term) | Q(genres__genre_name__icontains=term)
        
        movies = movies.filter(query).distinct()
        
        # 디버깅: 필터링된 영화 수 확인
        print(f"[장르 필터링] 결과: {movies.count()}개 영화")
    
    # 정렬
    if order_by == 'rating':
        movies = movies.order_by('-avg_rating', '-review_count')
    elif order_by == 'reviews':
        movies = movies.order_by('-review_count', '-avg_rating')
    else:
        movies = movies.order_by('-created_at')
    
    # 디버깅: 첫 번째 영화의 장르 확인
    if movies.exists():
        first_movie = movies.first()
        print(f"[디버깅] 첫 번째 영화: {first_movie.title}")
        print(f"[디버깅] 장르 개수: {first_movie.genres.count()}")
        if first_movie.genres.exists():
            print(f"[디버깅] 장르 목록: {[g.genre_name for g in first_movie.genres.all()]}")
        else:
            print(f"[디버깅] 장르가 없습니다!")
    
    serializer = MovieListSerializer(movies, many=True)
    
    # 디버깅: 직렬화된 첫 번째 영화의 장르 확인
    if serializer.data:
        print(f"[디버깅] 직렬화된 첫 번째 영화 장르: {serializer.data[0].get('genres', [])}")
    
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


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def recommended_movies(request):
    """사용자 선호 영화 기반 추천 영화"""
    if not request.user.is_authenticated:
        # 비로그인 사용자는 랜덤 영화 10개 반환
        import random
        all_movies = list(Movie.objects.prefetch_related('genres').all())
        if len(all_movies) > 10:
            movies = random.sample(all_movies, 10)
        else:
            movies = all_movies
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    user = request.user
    preferred_movies = user.preferred_movies.all()
    
    if not preferred_movies.exists():
        # 선호 영화가 없으면 평점 높은 영화 반환
        movies = Movie.objects.prefetch_related('genres').order_by('-avg_rating', '-review_count')[:12]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    # 선호 영화들의 장르 수집
    preferred_genre_ids = set()
    preferred_movie_ids = set(preferred_movies.values_list('id', flat=True))
    
    for movie in preferred_movies:
        for genre in movie.genres.all():
            preferred_genre_ids.add(genre.id)
    
    if not preferred_genre_ids:
        # 장르가 없으면 평점 높은 영화 반환
        movies = Movie.objects.prefetch_related('genres').exclude(
            id__in=preferred_movie_ids
        ).order_by('-avg_rating', '-review_count')[:12]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    # 선호 영화와 같은 장르를 가진 영화 찾기 (선호 영화 제외)
    # 장르 유사도가 높고 평점이 높은 순으로 정렬
    from django.db.models import Count, Q
    
    recommended = Movie.objects.filter(
        genres__id__in=preferred_genre_ids
    ).exclude(
        id__in=preferred_movie_ids
    ).annotate(
        genre_match_count=Count('genres', filter=Q(genres__id__in=preferred_genre_ids))
    ).distinct().order_by(
        '-genre_match_count',  # 장르 매칭 개수 (많을수록 유사)
        '-avg_rating',         # 평점 높은 순
        '-review_count'       # 리뷰 많은 순
    )[:12]
    
    # 결과가 12개 미만이면 평점 높은 영화로 채우기
    if recommended.count() < 12:
        additional = Movie.objects.exclude(
            id__in=[m.id for m in recommended] + list(preferred_movie_ids)
        ).order_by('-avg_rating', '-review_count')[:12 - recommended.count()]
        recommended = list(recommended) + list(additional)
    
    serializer = MovieListSerializer(recommended, many=True)
    return Response(serializer.data)