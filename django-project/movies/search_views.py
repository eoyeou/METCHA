"""
ChromaDB 기반 영화 검색 API
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from typing import List, Dict, Optional
import math

from reviews.embedding_utils import embed_text
from reviews.chroma_utils import search_similar_reviews
from .models import Movie
from .serializers import MovieListSerializer

User = get_user_model()

# 검색 파라미터 (추후 수정 가능)
SIMILARITY_THRESHOLD = 0.9  # 유사도 임계값 (원본 모델 사용 시 정상 범위)
SIMILARITY_WEIGHT = 0.7     # 유사도 가중치
PREFERENCE_WEIGHT = 0.3     # 취향 적합도 가중치


def calculate_preference_fit(user: User, movie: Movie) -> float:
    """
    사용자 취향 적합도 계산
    
    Args:
        user: 사용자 객체
        movie: 영화 객체
    
    Returns:
        취향 적합도 (0.0 ~ 1.0)
    """
    if user.avg_heaviness is None or user.avg_satisfaction is None:
        return 0.5  # 취향 정보가 없으면 중간값
    
    if movie.heaviness is None or movie.satisfaction is None:
        return 0.5  # 영화 정보가 없으면 중간값
    
    # H_fit = 1.0 - (|User_H - Movie_H| / 100)
    h_fit = 1.0 - (abs(user.avg_heaviness - movie.heaviness) / 100.0)
    
    # S_fit = 1.0 - (|User_S - Movie_S| / 100)
    s_fit = 1.0 - (abs(user.avg_satisfaction - movie.satisfaction) / 100.0)
    
    # S_personal = (H_fit + S_fit) / 2
    preference_fit = (h_fit + s_fit) / 2.0
    
    return max(0.0, min(1.0, preference_fit))  # 0~1 범위로 제한


def calculate_final_score(similarity: float, preference_fit: float) -> float:
    """
    최종 점수 계산
    
    Args:
        similarity: 유사도 점수 (0.0 ~ 1.0)
        preference_fit: 취향 적합도 (0.0 ~ 1.0)
    
    Returns:
        최종 점수
    """
    return similarity * SIMILARITY_WEIGHT + preference_fit * PREFERENCE_WEIGHT


@api_view(['POST'])
@permission_classes([AllowAny])
def semantic_search(request):
    """
    의미 기반 영화 검색 API
    
    Request Body:
        {
            "query": "검색어",
            "limit": 20 (선택, 기본값 20)
        }
    
    Response:
        {
            "results": [영화 리스트],
            "similarity_mode": "keyword" | "semantic",
            "max_similarity": 최대 유사도 점수
        }
    """
    query = request.data.get('query', '').strip()
    limit = int(request.data.get('limit', 20))
    
    if not query:
        return Response(
            {"error": "검색어를 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 1. 검색어를 임베딩으로 변환
        query_embedding = embed_text(query)
        
        # 2. ChromaDB에서 유사 리뷰 검색
        similar_reviews = search_similar_reviews(
            query_embedding=query_embedding,
            n_results=min(limit * 3, 100)  # 더 많이 가져와서 중복 제거
        )
        
        if not similar_reviews:
            return Response({
                "results": [],
                "similarity_mode": "semantic",
                "max_similarity": 0.0
            })
        
        # 3. 최대 유사도 점수 확인
        # ChromaDB 거리 메트릭 확인 및 변환
        distances = [r['distance'] for r in similar_reviews if r['distance'] is not None]
        if distances:
            min_distance = min(distances)
            
            # 거리 값에 따라 메트릭 판단
            # 코사인 거리: 0~2 범위
            # L2 거리: 0~무한대 (보통 0~10 정도)
            if min_distance <= 2.0:
                # 코사인 거리로 판단
                max_similarity = 1.0 - (min_distance / 2.0)
            else:
                # L2 거리로 판단 (정규화된 임베딩의 경우 보통 0~2 범위)
                # 거리를 유사도로 변환 (거리가 작을수록 유사)
                # exp(-distance) 또는 1/(1+distance) 사용
                max_similarity = 1.0 / (1.0 + min_distance)
            
            max_similarity = max(0.0, min(1.0, max_similarity))  # 0~1 범위로 제한
        else:
            max_similarity = 0.5  # 기본값
        
        # 4. 리뷰에서 영화 ID 추출 및 중복 제거
        movie_ids = set()
        review_to_movie = {}  # review_id -> movie_id 매핑
        
        for review in similar_reviews:
            movie_id = review['metadata'].get('movie_id')
            if movie_id:
                movie_id = int(movie_id)
                movie_ids.add(movie_id)
                review_to_movie[review['review_id']] = movie_id
        
        # 5. 영화 조회
        movies = Movie.objects.filter(id__in=movie_ids).prefetch_related('genres')
        movie_dict = {movie.id: movie for movie in movies}
        
        # 6. 유사도 모드 결정 (영화 제목과의 정확한 매칭 확인)
        is_keyword_mode = max_similarity >= SIMILARITY_THRESHOLD
        
        # 정확한 키워드 매칭 확인: 검색어가 영화 제목과 정확히 일치하거나 포함되는 경우
        if not is_keyword_mode:
            query_lower = query.lower().strip()
            # 상위 결과 중에서 검색어와 정확히 일치하는 영화가 있는지 확인
            for review in similar_reviews[:10]:  # 상위 10개만 확인
                movie_id = review_to_movie.get(review['review_id'])
                if movie_id and movie_id in movie_dict:
                    movie = movie_dict[movie_id]
                    # 한글 제목 또는 영문 제목과 정확히 일치하거나 포함되는지 확인
                    title_match = movie.title.lower() == query_lower or query_lower in movie.title.lower()
                    original_match = False
                    if movie.original_title:
                        original_match = movie.original_title.lower() == query_lower or query_lower in movie.original_title.lower()
                    
                    if title_match or original_match:
                        is_keyword_mode = True
                        print(f"[검색 모드] 정확한 키워드 매칭 감지: '{query}' -> '{movie.title}' (키워드 모드로 전환)")
                        break
        
        # 7. 결과 정렬 (영화별로 최고 점수만 유지)
        movie_scores = {}  # movie_id -> 최고 점수 정보
        # 사용자 인증 확인 (AnonymousUser가 아닌 경우)
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        for review in similar_reviews:
            movie_id = review_to_movie.get(review['review_id'])
            if not movie_id or movie_id not in movie_dict:
                continue
            
            movie = movie_dict[movie_id]
            
            # 거리를 유사도로 변환
            distance = review['distance'] if review['distance'] is not None else 1.0
            
            # 거리 메트릭에 따라 변환
            if distance <= 2.0:
                # 코사인 거리: 0~2 범위
                similarity = 1.0 - (distance / 2.0)
            else:
                # L2 거리: 거리를 유사도로 변환
                similarity = 1.0 / (1.0 + distance)
            
            similarity = max(0.0, min(1.0, similarity))  # 0~1 범위로 제한
            
            if is_keyword_mode:
                # 키워드 모드: 유사도만 사용
                final_score = similarity
            else:
                # 의미 모드: 유사도 + 취향 적합도
                if user and user.is_authenticated:
                    preference_fit = calculate_preference_fit(user, movie)
                    final_score = calculate_final_score(similarity, preference_fit)
                else:
                    # 비로그인 사용자는 유사도만 사용
                    final_score = similarity
            
            # 같은 영화의 여러 리뷰 중 최고 점수만 유지
            if movie_id not in movie_scores or final_score > movie_scores[movie_id]['final_score']:
                movie_scores[movie_id] = {
                    'movie': movie,
                    'similarity': similarity,
                    'final_score': final_score,
                    'review_id': review['review_id']
                }
        
        # 8. 최종 점수로 정렬
        results = list(movie_scores.values())
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 9. limit만큼만 반환
        unique_results = results[:limit]
        
        # 10. 직렬화 (순서 유지)
        movies_list = [r['movie'] for r in unique_results]
        serializer = MovieListSerializer(movies_list, many=True, context={'request': request})
        
        # 디버깅: 매트릭스 포함 여부 확인
        if '매트릭스' in query.lower() or 'matrix' in query.lower():
            matrix_idx = next((i for i, m in enumerate(movies_list) if '매트릭스' in m.title), -1)
            if matrix_idx >= 0:
                print(f"[검색 디버깅] 매트릭스 순위: {matrix_idx + 1}위 (총 {len(movies_list)}개)")
        
        return Response({
            "results": serializer.data,
            "similarity_mode": "keyword" if is_keyword_mode else "semantic",
            "max_similarity": max_similarity,
            "total_found": len(unique_results)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"검색 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

