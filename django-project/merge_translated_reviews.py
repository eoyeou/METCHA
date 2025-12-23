"""
여러 개의 번역된 JSON 파일을 하나로 병합

Kaggle에서 여러 파일로 번역한 경우 사용

사용 방법:
python merge_translated_reviews.py

또는

python merge_translated_reviews.py reviews_translated_part01.json reviews_translated_part02.json ...
"""
import json
import os
import sys
import glob


def merge_translated_files(output_file='reviews_translated.json'):
    """여러 번역 파일을 하나로 병합"""
    print("=" * 60)
    print("번역된 리뷰 파일 병합 중...")
    print("=" * 60)
    
    # 파일 찾기
    if len(sys.argv) > 1:
        # 명령줄 인자로 파일 목록 제공
        input_files = sys.argv[1:]
    else:
        # 자동으로 reviews_translated_part*.json 파일 찾기
        input_files = sorted(glob.glob('reviews_translated_part*.json'))
    
    if not input_files:
        print("[ERROR] 병합할 파일을 찾을 수 없습니다.")
        print("[INFO] reviews_translated_part*.json 파일이 있는지 확인하세요.")
        return None
    
    print(f"[INFO] {len(input_files)}개 파일 발견:")
    for f in input_files:
        print(f"  - {f}")
    
    # 모든 리뷰 병합
    all_reviews = []
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"[WARNING] 파일을 찾을 수 없습니다: {input_file}")
            continue
        
        print(f"\n[INFO] {input_file} 로드 중...")
        with open(input_file, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
            all_reviews.extend(reviews)
            print(f"[INFO] {len(reviews)}개 리뷰 로드 완료")
    
    # 결과 저장
    print(f"\n[INFO] {output_file} 저장 중...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_file) / 1024 / 1024
    print(f"[INFO] 병합 완료! 총 {len(all_reviews)}개 리뷰, 파일 크기: {file_size:.2f} MB")
    print(f"\n[INFO] 이제 import_translated_reviews.py로 DB에 반영하세요:")
    print(f"  python import_translated_reviews.py {output_file}")
    
    return all_reviews


if __name__ == '__main__':
    merge_translated_files()

