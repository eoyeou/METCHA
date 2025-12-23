"""
Kaggle에서 번역한 JSON 파일을 로컬 DB에 반영

사용 방법:
python import_translated_reviews.py reviews_translated.json

동작:
1. JSON 파일에서 번역 결과 읽기
2. Review 모델에서 해당 리뷰 찾기 (id로)
3. original_content에 원문 저장
4. content에 번역문 저장
"""
import os
import django
import json
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review
from tqdm import tqdm


def import_translated_reviews(json_file='reviews_translated.json'):
    """번역된 리뷰를 DB에 반영"""
    print("=" * 60)
    print("번역된 리뷰 DB 반영 중...")
    print("=" * 60)
    
    # JSON 파일 로드
    if not os.path.exists(json_file):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {json_file}")
        return
    
    print(f"[INFO] {json_file} 로드 중...")
    with open(json_file, 'r', encoding='utf-8') as f:
        translated_reviews = json.load(f)
    
    print(f"[INFO] 총 {len(translated_reviews)}개 번역 결과 로드 완료\n")
    
    # DB에 반영
    success_count = 0
    not_found_count = 0
    error_count = 0
    
    for item in tqdm(translated_reviews, desc="DB 반영 중"):
        review_id = item.get('id')
        original_content = item.get('original_content', '')
        translated_content = item.get('translated_content', '')
        
        if not review_id:
            print(f"\n[WARNING] 리뷰 ID가 없습니다: {item}")
            error_count += 1
            continue
        
        try:
            # 리뷰 찾기
            review = Review.objects.get(id=review_id)
            
            # 원문과 번역문 저장
            review.original_content = original_content
            review.content = translated_content
            review.save()
            
            success_count += 1
            
        except Review.DoesNotExist:
            print(f"\n[WARNING] 리뷰를 찾을 수 없습니다: ID {review_id}")
            not_found_count += 1
        except Exception as e:
            print(f"\n[ERROR] 리뷰 ID {review_id} 저장 실패: {str(e)}")
            error_count += 1
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("반영 완료!")
    print("=" * 60)
    print(f"성공: {success_count}개")
    print(f"리뷰 없음: {not_found_count}개")
    print(f"오류: {error_count}개")
    print("=" * 60)


def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'reviews_translated.json'
    
    import_translated_reviews(json_file)


if __name__ == '__main__':
    main()

