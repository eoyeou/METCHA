from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Watchlist
from .serializers import WatchlistSerializer
from movies.models import Movie


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def watchlist_list(request):
    """
    위시리스트 목록 조회 및 추가
    - GET: 사용자의 위시리스트 목록 조회
    - POST: 위시리스트에 영화 추가 (status='want'로 저장)
    """
    if request.method == 'GET':
        watchlists = Watchlist.objects.filter(user=request.user).select_related('movie').prefetch_related('movie__genres')
        serializer = WatchlistSerializer(watchlists, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        movie_id = request.data.get('movie_id')
        if not movie_id:
            return Response({'detail': 'movie_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        movie = get_object_or_404(Movie, pk=movie_id)
        
        # 이미 위시리스트에 있는지 확인
        watchlist, created = Watchlist.objects.get_or_create(
            user=request.user,
            movie=movie,
            defaults={'status': 'want'}
        )
        
        if not created:
            return Response({'detail': '이미 위시리스트에 추가된 영화입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = WatchlistSerializer(watchlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def watchlist_delete(request, movie_id):
    """위시리스트에서 영화 제거"""
    watchlist = get_object_or_404(Watchlist, user=request.user, movie_id=movie_id)
    watchlist.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def watchlist_check(request, movie_id):
    """특정 영화가 위시리스트에 있는지 확인"""
    is_in_watchlist = Watchlist.objects.filter(user=request.user, movie_id=movie_id).exists()
    return Response({'is_in_watchlist': is_in_watchlist})
