"""
로컬 DB에서 영어 리뷰를 추출하여 Kaggle용 JSON 파일 생성

사용 방법:
python export_reviews_for_kaggle.py

출력: reviews_input.json (Kaggle에 업로드할 파일)
"""
import os
import django
import json

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


def export_english_reviews(output_file='reviews_input.json', max_file_size_mb=0.9):
    """
    영어 리뷰 추출 (Kaggle 업로드 제한 대응)
    
    Args:
        output_file: 기본 출력 파일명 (실제로는 여러 파일 생성됨)
        max_file_size_mb: 최대 파일 크기 (MB, 기본값 0.9MB로 1MB 제한 안전 마진)
    """
    print("=" * 60)
    print("영어 리뷰 추출 중...")
    print("=" * 60)
    
    # 모든 리뷰 가져오기
    all_reviews = Review.objects.select_related('movie', 'user').all()
    
    # 영어 리뷰만 필터링
    english_reviews = []
    korean_count = 0
    
    for review in all_reviews:
        content = review.content
        
        # 이미 번역된 리뷰는 건너뛰기 (original_content가 있으면 이미 번역됨)
        if review.original_content:
            continue
        
        # 언어 감지
        lang = detect_language(content)
        
        if lang == 'en':
            english_reviews.append({
                'id': review.id,
                'content': content,
                'movie_id': review.movie.id,
                'user_id': review.user.id,
                'rating': review.rating,
            })
        elif lang == 'ko':
            korean_count += 1
    
    print(f"\n영어 리뷰: {len(english_reviews)}개")
    print(f"한국어 리뷰: {korean_count}개 (건너뜀)")
    print(f"이미 번역된 리뷰: {all_reviews.count() - len(english_reviews) - korean_count}개")
    
    # 파일 크기 제한에 맞춰 여러 파일로 분할
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    file_count = 0
    current_chunk = []
    current_size = 0
    
    # 임시 파일로 크기 측정
    temp_file = 'temp_size_check.json'
    
    for i, review in enumerate(english_reviews):
        # 현재 청크에 추가
        current_chunk.append(review)
        
        # 임시로 저장하여 크기 확인
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(current_chunk, f, ensure_ascii=False)
        current_size = os.path.getsize(temp_file)
        
        # 크기 제한 초과 시 현재 청크 저장하고 새 청크 시작
        if current_size > max_file_size_bytes and len(current_chunk) > 1:
            # 마지막 항목 제거 (다음 청크로)
            current_chunk.pop()
            
            # 현재 청크 저장
            chunk_filename = f"reviews_input_part{file_count + 1:02d}.json"
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                json.dump(current_chunk, f, ensure_ascii=False)
            
            file_size = os.path.getsize(chunk_filename) / 1024 / 1024
            print(f"[INFO] {chunk_filename} 저장 완료 ({len(current_chunk)}개 리뷰, {file_size:.2f} MB)")
            
            # 새 청크 시작
            file_count += 1
            current_chunk = [review]  # 마지막 항목을 새 청크에 추가
    
    # 마지막 청크 저장
    if current_chunk:
        chunk_filename = f"reviews_input_part{file_count + 1:02d}.json"
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            json.dump(current_chunk, f, ensure_ascii=False)
        
        file_size = os.path.getsize(chunk_filename) / 1024 / 1024
        print(f"[INFO] {chunk_filename} 저장 완료 ({len(current_chunk)}개 리뷰, {file_size:.2f} MB)")
        file_count += 1
    
    # 임시 파일 삭제
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print(f"\n[INFO] 총 {file_count}개 파일 생성 완료!")
    print(f"[INFO] 각 파일을 Kaggle에 업로드하거나, Kaggle Dataset으로 업로드하세요.")
    print(f"\n[팁] Kaggle Dataset 사용 방법:")
    print(f"  1. Kaggle → Datasets → New Dataset")
    print(f"  2. reviews_input_part*.json 파일들을 모두 업로드")
    print(f"  3. Notebook에서 Dataset 추가하여 사용")
    
    return english_reviews


if __name__ == '__main__':
    export_english_reviews()

