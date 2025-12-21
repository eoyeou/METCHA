from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Movie
from .serializers import MovieDetailSerializer, MovieListSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        return MovieDetailSerializer
    
    def list(self, request):
        """영화 목록 조회"""
        movies = Movie.objects.all().prefetch_related('genres').order_by('-created_at')
        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """영화 상세 정보 조회"""
        movie = get_object_or_404(
            Movie.objects.prefetch_related('genres', 'reviews__user'), 
            pk=pk
        )
        serializer = self.get_serializer(movie)
        return Response(serializer.data)