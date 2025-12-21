from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Review
from .serializers import ReviewCreateSerializer, ReviewUpdateSerializer
from movies.serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def create(self, request):
        """리뷰 작성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 이미 리뷰를 작성했는지 확인
        movie_id = serializer.validated_data['movie'].id
        if Review.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"detail": "이미 이 영화에 리뷰를 작성하셨습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review = serializer.save()
        return Response(
            ReviewSerializer(review).data, 
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """리뷰 수정"""
        review = get_object_or_404(Review, pk=pk)
        
        if review.user != request.user:
            return Response(
                {"detail": "본인의 리뷰만 수정할 수 있습니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ReviewSerializer(review).data)
    
    def destroy(self, request, pk=None):
        """리뷰 삭제"""
        review = get_object_or_404(Review, pk=pk)
        
        if review.user != request.user:
            return Response(
                {"detail": "본인의 리뷰만 삭제할 수 있습니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)