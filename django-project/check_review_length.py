"""
DB에 있는 영어 리뷰의 총 글자 수 확인
"""
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review


def detect_language(text):
    """텍스트 언어 감지 (간단한 휴리스틱)"""
    # 한글이 포함되어 있으면 한국어로 간주
    if re.search(r'[가-힣]', text):
        return 'ko'
    
    # 영어로 간주
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    
    return 'unknown'


def check_review_lengths():
    """리뷰 길이 통계 확인"""
    print("=" * 60)
    print("리뷰 글자 수 통계")
    print("=" * 60)
    
    # original_content 필드가 없을 수 있으므로 values()로 content만 가져오기
    all_reviews = Review.objects.values_list('content', flat=True)
    total_reviews = Review.objects.count()
    
    print(f"\n전체 리뷰 수: {total_reviews}개\n")
    
    # 언어별 분류
    english_reviews = []
    korean_reviews = []
    other_reviews = []
    
    for content in all_reviews:
        lang = detect_language(content)
        if lang == 'en':
            english_reviews.append(content)
        elif lang == 'ko':
            korean_reviews.append(content)
        else:
            other_reviews.append(content)
    
    print(f"영어 리뷰: {len(english_reviews)}개")
    print(f"한국어 리뷰: {len(korean_reviews)}개")
    print(f"기타: {len(other_reviews)}개\n")
    
    # 영어 리뷰 글자 수 계산
    total_english_chars = 0
    english_review_lengths = []
    
    for content in english_reviews:
        char_count = len(content)
        total_english_chars += char_count
        english_review_lengths.append(char_count)
    
    # 통계
    if english_review_lengths:
        avg_length = total_english_chars / len(english_reviews)
        max_length = max(english_review_lengths)
        min_length = min(english_review_lengths)
        
        print("=" * 60)
        print("영어 리뷰 글자 수 통계")
        print("=" * 60)
        print(f"총 글자 수: {total_english_chars:,}자")
        print(f"평균 글자 수: {avg_length:.1f}자")
        print(f"최대 글자 수: {max_length:,}자")
        print(f"최소 글자 수: {min_length:,}자")
        print(f"리뷰 개수: {len(english_reviews)}개")
        
        # Google Translate API 무료 할당량 비교
        print("\n" + "=" * 60)
        print("Google Translate API 할당량 비교")
        print("=" * 60)
        free_quota = 500000  # 월 50만자 무료
        print(f"무료 할당량: {free_quota:,}자/월")
        print(f"필요한 글자 수: {total_english_chars:,}자")
        
        if total_english_chars <= free_quota:
            remaining = free_quota - total_english_chars
            print(f"[OK] 무료 할당량 내에서 번역 가능!")
            print(f"  남은 할당량: {remaining:,}자")
        else:
            excess = total_english_chars - free_quota
            cost_per_1m = 20  # 100만자당 $20 (예상)
            estimated_cost = (excess / 1000000) * cost_per_1m
            print(f"[WARNING] 무료 할당량 초과!")
            print(f"  초과 분량: {excess:,}자")
            print(f"  예상 비용: 약 ${estimated_cost:.2f} (100만자당 $20 기준)")
        
        # 비용 계산 (정확한 가격은 Google Cloud 문서 확인 필요)
        print("\n" + "=" * 60)
        print("예상 비용 (참고용)")
        print("=" * 60)
        print("Google Translate API 가격:")
        print("  - 월 50만자: 무료")
        print("  - 초과분: 100만자당 약 $20")
        
        if total_english_chars > free_quota:
            excess_chars = total_english_chars - free_quota
            excess_millions = excess_chars / 1000000
            estimated_cost = excess_millions * 20
            print(f"\n예상 비용: ${estimated_cost:.2f}")
        else:
            print(f"\n예상 비용: $0 (무료 할당량 내)")
    
    else:
        print("영어 리뷰가 없습니다.")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    check_review_lengths()

