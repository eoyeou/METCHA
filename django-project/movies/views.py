from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Movie
from .serializers import MovieDetailSerializer, MovieListSerializer


@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.all().prefetch_related('genres').order_by('-created_at')
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