"""
Kaggle Notebook에서 바로 실행할 수 있는 완전한 번역 스크립트

사용 방법:
1. Kaggle Notebook 생성 (GPU 활성화 필수!)
2. Dataset 추가 (reviews_input_part*.json 파일들)
3. 이 코드를 셀에 붙여넣고 실행
"""

# 필요한 라이브러리 설치
import subprocess
import sys

def install_packages():
    """필요한 패키지 설치"""
    packages = ['transformers', 'torch', 'tqdm']
    for package in packages:
        try:
            __import__(package)
            print(f"[OK] {package} 이미 설치됨")
        except ImportError:
            print(f"[INFO] {package} 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[OK] {package} 설치 완료")

install_packages()

# ============================================
# 아래는 kaggle_translate_reviews.py의 모든 코드
# ============================================

import json
import re
import torch
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from tqdm import tqdm
import os


def detect_language(text):
    """텍스트 언어 감지"""
    if re.search(r'[가-힣]', text):
        return 'ko'
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    return 'unknown'


def translate_with_mbart(text, tokenizer, model, device='cuda'):
    """
    mbart-large-50 모델로 번역
    
    Args:
        text: 번역할 텍스트
        tokenizer: MBart50TokenizerFast
        model: MBartForConditionalGeneration
        device: 'cuda' or 'cpu'
    
    Returns:
        번역된 텍스트 (한국어)
    """
    try:
        # 언어 코드 설정 (영어 -> 한국어)
        tokenizer.src_lang = "en_XX"
        
        # 텍스트 인코딩
        encoded = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        
        # 번역 생성
        with torch.no_grad():
            generated_tokens = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.lang_code_to_id["ko_KR"],
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
        
        # 디코딩
        translated = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        return translated
        
    except Exception as e:
        print(f"  [ERROR] 번역 실패: {str(e)}")
        return None


def find_kaggle_dataset_path(filename):
    """
    Kaggle Dataset 경로 찾기
    
    Args:
        filename: 찾을 파일명
    
    Returns:
        파일의 전체 경로 또는 None
    """
    import glob
    
    # Kaggle Dataset 경로 패턴들
    search_paths = [
        f"/kaggle/input/*/{filename}",  # 일반적인 Kaggle Dataset 경로
        f"/kaggle/input/**/{filename}",  # 하위 디렉토리 포함
        filename,  # 현재 디렉토리
        f"./{filename}",  # 현재 디렉토리 (명시적)
    ]
    
    for path_pattern in search_paths:
        matches = glob.glob(path_pattern, recursive=True)
        if matches:
            return matches[0]
    
    return None


def load_reviews(input_file='reviews_input.json', use_multiple_files=True):
    """
    리뷰 데이터 로드
    
    Args:
        input_file: 단일 파일명 또는 기본 파일명 (use_multiple_files=True일 때)
        use_multiple_files: 여러 파일에서 로드할지 여부
    """
    all_reviews = []
    
    if use_multiple_files:
        # 여러 파일에서 로드 (reviews_input_part01.json, part02.json, ...)
        print(f"[INFO] 여러 파일에서 리뷰 데이터 로드 중...")
        part_num = 1
        found_files = []
        
        while True:
            filename = f"reviews_input_part{part_num:02d}.json"
            
            # Kaggle Dataset 경로에서 파일 찾기
            file_path = find_kaggle_dataset_path(filename)
            
            if not file_path or not os.path.exists(file_path):
                break
            
            print(f"[INFO] {file_path} 로드 중...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reviews = json.load(f)
                    all_reviews.extend(reviews)
                    found_files.append(file_path)
                    print(f"[INFO] {len(reviews)}개 리뷰 로드 완료")
            except Exception as e:
                print(f"[ERROR] {file_path} 로드 실패: {str(e)}")
                break
            
            part_num += 1
        
        if all_reviews:
            print(f"[INFO] 총 {len(all_reviews)}개 리뷰 로드 완료 (파일 {len(found_files)}개)")
            print(f"[INFO] 찾은 파일: {', '.join([os.path.basename(f) for f in found_files])}")
        else:
            print(f"[ERROR] 리뷰 파일을 찾을 수 없습니다.")
            print(f"[INFO] Dataset이 추가되었는지 확인하세요.")
            print(f"[INFO] /kaggle/input/ 디렉토리 내용:")
            if os.path.exists("/kaggle/input"):
                import glob
                datasets = glob.glob("/kaggle/input/*")
                for ds in datasets:
                    print(f"  - {ds}")
                    files = glob.glob(f"{ds}/*.json")
                    for f in files:
                        print(f"    - {os.path.basename(f)}")
            return None
    else:
        # 단일 파일에서 로드
        print(f"[INFO] 리뷰 데이터 로드 중: {input_file}")
        
        # Kaggle Dataset 경로에서 파일 찾기
        file_path = find_kaggle_dataset_path(input_file)
        
        if not file_path:
            file_path = input_file  # 찾지 못하면 원본 경로 사용
        
        if not os.path.exists(file_path):
            print(f"[ERROR] 파일을 찾을 수 없습니다: {input_file}")
            print(f"[INFO] Dataset이 추가되었는지 확인하세요.")
            if os.path.exists("/kaggle/input"):
                import glob
                print(f"[INFO] /kaggle/input/ 디렉토리 내용:")
                datasets = glob.glob("/kaggle/input/*")
                for ds in datasets:
                    print(f"  - {ds}")
            return None
        
        print(f"[INFO] 파일 경로: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            all_reviews = json.load(f)
        
        print(f"[INFO] 총 {len(all_reviews)}개 리뷰 로드 완료")
    
    return all_reviews


def translate_reviews(reviews, use_gpu=True, use_quantized=False):
    """리뷰 번역"""
    # GPU 사용 가능 여부 확인
    device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
    print(f"[INFO] 디바이스: {device}")
    
    if device == 'cpu':
        print("[WARNING] CPU 모드입니다. 매우 느릴 수 있습니다.")
        print("[WARNING] GPU가 활성화되었는지 확인하세요: Settings → Accelerator → GPU")
    
    # 모델 로드
    if use_quantized:
        model_name = "RichardErkhov/facebook_-_mbart-large-50-many-to-many-mmt-4bits"
        print(f"[INFO] 양자화 버전 사용: {model_name}")
    else:
        model_name = "facebook/mbart-large-50-many-to-many-mmt"
        print(f"[INFO] 모델 로딩 중: {model_name}")
    
    print("[INFO] 토크나이저 로딩 중...")
    tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
    
    print("[INFO] 모델 로딩 중... (시간이 걸릴 수 있습니다)")
    model = MBartForConditionalGeneration.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    print("[INFO] 모델 로딩 완료!")
    
    # 영어 리뷰만 필터링
    english_reviews = []
    for review in reviews:
        content = review.get('content', '')
        if detect_language(content) == 'en':
            english_reviews.append(review)
    
    print(f"[INFO] 영어 리뷰: {len(english_reviews)}개")
    print(f"[INFO] 한국어 리뷰: {len(reviews) - len(english_reviews)}개 (건너뜀)")
    
    # 번역 수행
    translated_reviews = []
    failed_count = 0
    
    print("\n[INFO] 번역 시작...")
    for review in tqdm(english_reviews, desc="번역 중"):
        original_content = review.get('content', '')
        
        # 번역 수행
        translated_content = translate_with_mbart(original_content, tokenizer, model, device)
        
        if translated_content:
            result = {
                'id': review.get('id'),
                'original_content': original_content,
                'translated_content': translated_content,
                'movie_id': review.get('movie_id'),
                'user_id': review.get('user_id'),
            }
            translated_reviews.append(result)
        else:
            failed_count += 1
            print(f"\n[WARNING] 리뷰 ID {review.get('id')} 번역 실패")
    
    print(f"\n[INFO] 번역 완료!")
    print(f"[INFO] 성공: {len(translated_reviews)}개")
    print(f"[INFO] 실패: {failed_count}개")
    
    return translated_reviews


def save_results(translated_reviews, output_file='reviews_translated.json', split_files=True):
    """
    번역 결과 저장
    
    Args:
        translated_reviews: 번역된 리뷰 리스트
        output_file: 기본 출력 파일명
        split_files: 여러 파일로 분할할지 여부 (Kaggle 다운로드 제한 대응)
    """
    if split_files and len(translated_reviews) > 500:
        # 여러 파일로 분할 저장 (각각 약 1MB 미만)
        print(f"\n[INFO] 결과를 여러 파일로 저장 중...")
        
        chunk_size = 500  # 각 파일당 약 500개 리뷰
        file_count = 0
        
        for i in range(0, len(translated_reviews), chunk_size):
            chunk = translated_reviews[i:i + chunk_size]
            chunk_filename = f"reviews_translated_part{file_count + 1:02d}.json"
            
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(chunk_filename) / 1024 / 1024
            print(f"[INFO] {chunk_filename} 저장 완료 ({len(chunk)}개 리뷰, {file_size:.2f} MB)")
            file_count += 1
        
        print(f"\n[INFO] 총 {file_count}개 파일 저장 완료!")
        print(f"[INFO] 모든 파일을 다운로드하여 로컬에서 merge_translated_reviews.py로 병합하세요.")
    else:
        # 단일 파일로 저장
        print(f"\n[INFO] 결과 저장 중: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_reviews, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 저장 완료! 총 {len(translated_reviews)}개 리뷰")
        print(f"[INFO] 파일 크기: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")


def main():
    """메인 함수"""
    print("=" * 60)
    print("Kaggle 리뷰 번역 스크립트")
    print("=" * 60)
    
    # GPU 확인
    print(f"\n[INFO] GPU 확인 중...")
    print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU 이름: {torch.cuda.get_device_name(0)}")
        print(f"GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("[WARNING] GPU가 감지되지 않았습니다!")
        print("[WARNING] Settings → Accelerator → GPU로 설정하세요.")
    
    # 설정
    input_file = 'reviews_input.json'
    output_file = 'reviews_translated.json'
    use_gpu = True
    use_quantized = False  # 메모리가 부족하면 True로 변경
    use_multiple_files = True  # 여러 파일에서 로드할지 여부
    split_output_files = True  # 출력 파일도 여러 개로 분할할지 여부
    
    # 리뷰 데이터 로드
    reviews = load_reviews(input_file, use_multiple_files=use_multiple_files)
    if not reviews:
        print("\n[ERROR] 리뷰 데이터를 로드할 수 없습니다.")
        print("[INFO] Dataset이 추가되었는지 확인하세요.")
        return
    
    # 번역 수행
    translated_reviews = translate_reviews(reviews, use_gpu=use_gpu, use_quantized=use_quantized)
    
    # 결과 저장
    if translated_reviews:
        save_results(translated_reviews, output_file, split_files=split_output_files)
        print("\n[SUCCESS] 모든 작업 완료!")
        if split_output_files:
            print(f"[INFO] reviews_translated_part*.json 파일들을 다운로드하여 로컬로 가져오세요.")
            print(f"[INFO] 로컬에서 merge_translated_reviews.py로 병합하세요.")
        else:
            print(f"[INFO] {output_file} 파일을 다운로드하여 로컬로 가져오세요.")
    else:
        print("\n[ERROR] 번역된 리뷰가 없습니다.")


# 실행
if __name__ == '__main__':
    main()

