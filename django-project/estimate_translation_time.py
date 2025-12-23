"""
번역 시간 예상 계산 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review
import re


def detect_language(text):
    """텍스트 언어 감지"""
    if re.search(r'[가-힣]', text):
        return 'ko'
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    return 'unknown'


def estimate_translation_time():
    """번역 시간 예상"""
    print("=" * 60)
    print("번역 시간 예상 계산")
    print("=" * 60)
    
    # 영어 리뷰 찾기
    all_reviews = Review.objects.values_list('content', flat=True)
    english_reviews = [r for r in all_reviews if detect_language(r) == 'en']
    
    total_chars = sum(len(r) for r in english_reviews)
    total_reviews = len(english_reviews)
    avg_length = total_chars / total_reviews if total_reviews > 0 else 0
    
    print(f"\n영어 리뷰: {total_reviews}개")
    print(f"총 글자 수: {total_chars:,}자")
    print(f"평균 글자 수: {avg_length:.1f}자\n")
    
    # 번역 방법별 시간 예상
    print("=" * 60)
    print("번역 방법별 예상 시간")
    print("=" * 60)
    
    # 1. googletrans
    # 약 0.5-1초/리뷰 (짧은 리뷰), API 제한 있음
    googletrans_time = total_reviews * 1.0  # 초
    googletrans_hours = googletrans_time / 3600
    print(f"\n1. googletrans (무료)")
    print(f"   예상 시간: {googletrans_hours:.1f}시간 ({googletrans_time/60:.1f}분)")
    print(f"   제한: 하루 약 15,000자 (여러 날 필요)")
    
    # 2. mbart CPU
    # 약 10-30초/리뷰 (CPU)
    mbart_cpu_fast = total_reviews * 10  # 초 (최적의 경우)
    mbart_cpu_slow = total_reviews * 30  # 초 (최악의 경우)
    mbart_cpu_fast_hours = mbart_cpu_fast / 3600
    mbart_cpu_slow_hours = mbart_cpu_slow / 3600
    print(f"\n2. mbart (CPU)")
    print(f"   예상 시간: {mbart_cpu_fast_hours:.1f} ~ {mbart_cpu_slow_hours:.1f}시간")
    print(f"   ({mbart_cpu_fast/60:.1f} ~ {mbart_cpu_slow/60:.1f}분)")
    print(f"   [WARNING] 매우 느림! 하루 종일 걸릴 수 있음")
    
    # 3. mbart GPU (RTX 3060 등)
    # 약 1-2초/리뷰 (GPU)
    mbart_gpu_fast = total_reviews * 1  # 초
    mbart_gpu_slow = total_reviews * 2  # 초
    mbart_gpu_fast_hours = mbart_gpu_fast / 3600
    mbart_gpu_slow_hours = mbart_gpu_slow / 3600
    print(f"\n3. mbart (GPU - RTX 3060 등)")
    print(f"   예상 시간: {mbart_gpu_fast_hours:.1f} ~ {mbart_gpu_slow_hours:.1f}시간")
    print(f"   ({mbart_gpu_fast/60:.1f} ~ {mbart_gpu_slow/60:.1f}분)")
    print(f"   [OK] 권장 방법")
    
    # 4. mbart GPU (Kaggle T4)
    # T4는 RTX 3060보다 약간 느림, 약 1.5-3초/리뷰
    mbart_t4_fast = total_reviews * 1.5  # 초
    mbart_t4_slow = total_reviews * 3  # 초
    mbart_t4_fast_hours = mbart_t4_fast / 3600
    mbart_t4_slow_hours = mbart_t4_slow / 3600
    print(f"\n4. mbart (GPU - Kaggle T4)")
    print(f"   예상 시간: {mbart_t4_fast_hours:.1f} ~ {mbart_t4_slow_hours:.1f}시간")
    print(f"   ({mbart_t4_fast/60:.1f} ~ {mbart_t4_slow/60:.1f}분)")
    print(f"   [OK] Kaggle 무료 GPU 사용 가능")
    
    # 5. Google Translate API
    # 매우 빠름, 하지만 비용 발생
    google_api_time = total_reviews * 0.5  # 초 (API 호출 시간)
    google_api_hours = google_api_time / 3600
    print(f"\n5. Google Translate API")
    print(f"   예상 시간: {google_api_hours:.1f}시간 ({google_api_time/60:.1f}분)")
    print(f"   비용: 약 $17.81 (초과분)")
    
    print("\n" + "=" * 60)
    print("추천 방법")
    print("=" * 60)
    print("1. Kaggle T4 GPU: mbart (T4) - 약 30분~1시간 (무료!)")
    print("2. 일반 GPU: mbart (GPU) - 약 1-2시간")
    print("3. GPU가 없다면: googletrans - 여러 날에 나눠서")
    print("4. 빠른 번역 필요: Google Translate API - 약 30분, 비용 발생")
    print("5. CPU + mbart: 비추천 (하루 종일 걸림)")
    print("=" * 60)
    print("\n[Kaggle T4 사용 팁]")
    print("- Kaggle Notebook에서 무료 GPU 사용 가능 (주당 30시간)")
    print("- 스크립트를 Kaggle에 업로드하고 GPU 활성화 후 실행")
    print("- 약 30분~1시간 내에 139만자 번역 완료 가능")
    print("=" * 60)

if __name__ == '__main__':
    estimate_translation_time()

