from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg

from .models import User, PreferenceReport, Follow
from .serializers import (
    UserProfileSerializer, 
    UserReviewSerializer, 
    PreferenceReportSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSimpleSerializer
)
from reviews.models import Review


@api_view(['GET'])
@permission_classes([AllowAny])
def profile_detail(request, user_id=None):
    """사용자 프로필 정보 조회"""
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        # 로그인한 사용자 또는 첫 번째 유저
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.first()
            if not user:
                return Response(
                    {"detail": "사용자를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    serializer = UserProfileSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def profile_reviews(request, user_id=None):
    """사용자 리뷰 목록 조회"""
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.first()
            if not user:
                return Response(
                    {"detail": "사용자를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    reviews = Review.objects.filter(user=user).select_related('movie').order_by('-created_at')
    serializer = UserReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def preference_report(request, user_id=None):
    """취향 리포트 조회 또는 생성"""
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.first()
            if not user:
                return Response(
                    {"detail": "사용자를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    if request.method == 'GET':
        # 최신 리포트 조회
        report = PreferenceReport.objects.filter(user=user).order_by('-generated_at').first()
        if not report:
            return Response(
                {"detail": "취향 리포트가 없습니다. 생성해주세요."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PreferenceReportSerializer(report)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # 취향 리포트 생성
        print(f"[취향 리포트 생성] 사용자: {user.username} (ID: {user.id})")
        reviews = Review.objects.filter(user=user).select_related('movie').prefetch_related('movie__genres')
        
        print(f"[취향 리포트 생성] 리뷰 개수: {reviews.count()}")
        
        if not reviews.exists():
            print(f"[취향 리포트 생성] 리뷰가 없어서 리포트 생성 불가")
            return Response(
                {"detail": "리뷰가 없어서 취향 리포트를 생성할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 리뷰 상세 정보 로그
        print(f"[취향 리포트 생성] 리뷰 상세:")
        for review in reviews:
            genres = list(review.movie.genres.all().values_list('genre_name', flat=True))
            print(f"  - {review.movie.title}: {review.rating}점, 장르: {genres}, 감독: {review.movie.director}")
        
        # 장르별 선호도 분석
        genre_counts = {}
        for review in reviews:
            genres = review.movie.genres.all()
            print(f"[취향 리포트 생성] 리뷰 {review.id}의 장르 개수: {genres.count()}")
            for genre in genres:
                genre_name = genre.genre_name
                genre_counts[genre_name] = genre_counts.get(genre_name, 0) + 1
                print(f"[취향 리포트 생성] 장르 추가: {genre_name} (현재 카운트: {genre_counts[genre_name]})")
        
        # 정규화 (퍼센트로 변환)
        total_reviews = reviews.count()
        genre_distribution = {
            genre: round((count / total_reviews) * 100, 1)
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        
        print(f"[취향 리포트 생성] 장르 분포: {genre_distribution}")
        print(f"[취향 리포트 생성] 장르 카운트 원본: {genre_counts}")
        
        # 평균 별점 분포 (간단 버전)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        print(f"[취향 리포트 생성] 평균 별점: {avg_rating}")
        
        # 감독 선호도
        director_counts = {}
        for review in reviews:
            director = review.movie.director
            print(f"[취향 리포트 생성] 리뷰 {review.id}의 감독: {director}")
            if director and director != "정보 없음":
                director_counts[director] = director_counts.get(director, 0) + 1
        
        director_preferences = dict(sorted(
            director_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5])
        print(f"[취향 리포트 생성] 감독 선호도: {director_preferences}")
        
        # 높은 평점 영화 (4.0 이상)
        top_rated = list(reviews.filter(rating__gte=4.0).values_list('movie__title', flat=True)[:5])
        print(f"[취향 리포트 생성] 높은 평점 영화: {top_rated}")
        
        # 무드 분석 (간단 버전 - 나중에 개선)
        mood_analysis = {
            '평균 평점': round(avg_rating, 1),
            '총 리뷰 수': total_reviews,
        }
        print(f"[취향 리포트 생성] 무드 분석: {mood_analysis}")
        
        # 한 줄 요약
        top_genre = list(genre_distribution.keys())[0] if genre_distribution else "다양한"
        summary = f"{top_genre} 장르를 좋아하고, 평균 별점이 {round(avg_rating, 1)}점이에요!"
        
        print(f"[취향 리포트 생성] 리포트 데이터 준비 완료")
        print(f"[취향 리포트 생성] 요약: {summary}")
        
        # 리포트 생성
        try:
            report_data = {
                'user': user,
                'genre_distribution': genre_distribution,
                'mood_analysis': mood_analysis,
                'director_preferences': director_preferences,
                'top_rated_movies': list(top_rated),
                'summary': summary
            }
            print(f"[취향 리포트 생성] 리포트 데이터: {report_data}")
            
            report = PreferenceReport.objects.create(**report_data)
            print(f"[취향 리포트 생성] 리포트 생성 성공! ID: {report.id}, 생성일: {report.generated_at}")
            
            # 생성된 리포트 확인
            saved_report = PreferenceReport.objects.get(id=report.id)
            print(f"[취향 리포트 생성] 저장된 리포트 확인:")
            print(f"  - 장르 분포: {saved_report.genre_distribution}")
            print(f"  - 무드 분석: {saved_report.mood_analysis}")
            print(f"  - 감독 선호도: {saved_report.director_preferences}")
            print(f"  - 높은 평점 영화: {saved_report.top_rated_movies}")
            print(f"  - 요약: {saved_report.summary}")
            
        except Exception as e:
            print(f"[취향 리포트 생성] 리포트 생성 실패: {e}")
            import traceback
            print(f"[취향 리포트 생성] 에러 상세: {traceback.format_exc()}")
            return Response(
                {"detail": f"리포트 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = PreferenceReportSerializer(report)
        print(f"[취향 리포트 생성] Serializer 데이터: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """회원가입"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': '회원가입이 완료되었습니다.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """로그인"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': '로그인 성공'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃 (토큰 삭제)"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({'message': '로그아웃되었습니다.'}, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """팔로우/언팔로우"""
    print(f"[팔로우 API] 요청 메서드: {request.method}, user_id: {user_id}")
    print(f"[팔로우 API] 현재 사용자: {request.user.username if request.user.is_authenticated else '인증 안됨'}")
    
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    print(f"[팔로우 API] 대상 사용자: {target_user.username}")
    
    # 자기 자신 팔로우 방지
    if current_user.id == target_user.id:
        print(f"[팔로우 API] 자기 자신 팔로우 시도 차단")
        return Response(
            {"detail": "자기 자신을 팔로우할 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'POST':
        # 팔로우
        print(f"[팔로우 API] 팔로우 시도: {current_user.username} -> {target_user.username}")
        follow, created = Follow.objects.get_or_create(
            follower=current_user,
            following=target_user
        )
        if created:
            print(f"[팔로우 API] 팔로우 성공: {current_user.username} -> {target_user.username}")
            return Response(
                {"message": f"{target_user.username}님을 팔로우했습니다."},
                status=status.HTTP_201_CREATED
            )
        else:
            print(f"[팔로우 API] 이미 팔로우 중: {current_user.username} -> {target_user.username}")
            return Response(
                {"detail": "이미 팔로우 중입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    elif request.method == 'DELETE':
        # 언팔로우
        print(f"[팔로우 API] 언팔로우 시도: {current_user.username} -> {target_user.username}")
        follow = Follow.objects.filter(
            follower=current_user,
            following=target_user
        ).first()
        if follow:
            follow.delete()
            print(f"[팔로우 API] 언팔로우 성공: {current_user.username} -> {target_user.username}")
            return Response(
                {"message": f"{target_user.username}님을 언팔로우했습니다."},
                status=status.HTTP_200_OK
            )
        else:
            print(f"[팔로우 API] 팔로우하지 않은 사용자 언팔로우 시도")
            return Response(
                {"detail": "팔로우하지 않은 사용자입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def followers_list(request, user_id):
    """팔로워 목록 조회"""
    user = get_object_or_404(User, id=user_id)
    # 팔로워 목록: 이 사용자를 팔로우하는 사람들
    # Follow 모델에서 following=user인 경우의 follower들을 가져옴
    follower_ids = Follow.objects.filter(following=user).values_list('follower', flat=True)
    followers = User.objects.filter(id__in=follower_ids).exclude(id=user.id).distinct()
    
    serializer = UserSimpleSerializer(
        followers, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def following_list(request, user_id):
    """팔로잉 목록 조회"""
    user = get_object_or_404(User, id=user_id)
    # 팔로잉 목록: 이 사용자가 팔로우하는 사람들
    # Follow 모델에서 follower=user인 경우의 following들을 가져옴
    following_ids = Follow.objects.filter(follower=user).values_list('following', flat=True)
    following = User.objects.filter(id__in=following_ids).exclude(id=user.id).distinct()
    
    serializer = UserSimpleSerializer(
        following, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)
