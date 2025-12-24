from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Review, ReviewLike
from .serializers import ReviewCreateSerializer, ReviewUpdateSerializer
from movies.serializers import ReviewSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_create(request):
    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # 이미 리뷰를 작성했는지 확인
        movie_id = serializer.validated_data['movie'].id
        user = request.user
        
        if Review.objects.filter(user=user, movie_id=movie_id).exists():
            return Response(
                {"detail": "이미 이 영화에 리뷰를 작성하셨습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review = serializer.save(user=user)
        
        # 리뷰 생성 후 사용자 취향 점수 업데이트
        try:
            user.update_preference_scores()
        except Exception as e:
            print(f"[경고] 사용자 취향 점수 업데이트 실패: {e}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def review_update_or_delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    # 본인 확인
    if review.user != request.user:
        return Response(
            {"detail": "본인의 리뷰만 수정/삭제할 수 있습니다."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # PUT, PATCH 처리
    serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        # 리뷰 수정 후 사용자 취향 점수 업데이트
        try:
            review.user.update_preference_scores()
        except Exception as e:
            print(f"[경고] 사용자 취향 점수 업데이트 실패: {e}")
        
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_like(request, review_pk):
    """리뷰 좋아요/좋아요 취소"""
    review = get_object_or_404(Review, pk=review_pk)
    user = request.user
    
    # 이미 좋아요를 눌렀는지 확인
    like, created = ReviewLike.objects.get_or_create(
        user=user,
        review=review
    )
    
    if not created:
        # 이미 좋아요를 눌렀다면 취소
        like.delete()
        review.likes_count = max(0, review.likes_count - 1)
        review.save(update_fields=['likes_count'])
        is_liked = False
    else:
        # 좋아요 추가
        review.likes_count += 1
        review.save(update_fields=['likes_count'])
        is_liked = True
    
    return Response({
        'is_liked': is_liked,
        'likes_count': review.likes_count
    })