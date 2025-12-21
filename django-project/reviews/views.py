from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Review
from .serializers import ReviewCreateSerializer, ReviewUpdateSerializer
from movies.serializers import ReviewSerializer


@api_view(['POST'])
@permission_classes([AllowAny])  # 임시로 모두 허용 (나중에 IsAuthenticated로 변경)
def review_create(request):
    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # 이미 리뷰를 작성했는지 확인
        movie_id = serializer.validated_data['movie'].id
        
        # 임시: 첫 번째 유저 사용 (나중에 request.user로 변경)
        from accounts.models import User
        user = User.objects.first()
        
        if Review.objects.filter(user=user, movie_id=movie_id).exists():
            return Response(
                {"detail": "이미 이 영화에 리뷰를 작성하셨습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def review_update(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    # 본인 확인 (임시로 주석 처리)
    # if review.user != request.user:
    #     return Response(
    #         {"detail": "본인의 리뷰만 수정할 수 있습니다."}, 
    #         status=status.HTTP_403_FORBIDDEN
    #     )
    
    serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(ReviewSerializer(review).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def review_delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    # 본인 확인 (임시로 주석 처리)
    # if review.user != request.user:
    #     return Response(
    #         {"detail": "본인의 리뷰만 삭제할 수 있습니다."}, 
    #         status=status.HTTP_403_FORBIDDEN
    #     )
    
    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)