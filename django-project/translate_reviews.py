"""
영어 리뷰를 한국어로 번역하는 스크립트

번역 방법:
1. deep-translator (무료, 간단) - 추천 (구 googletrans 대체)
2. Papago API (네이버, 한국어 번역 품질 좋음)
   ⚠️ 제한: 한 번에 최대 5,000자, 하루 최대 10,000자
3. Google Translate API (유료)
4. mbart-large-50 (Hugging Face, 오프라인, 무료)
   - GPU 권장 (약 6-8GB VRAM)
   - CPU에서도 실행 가능 (느림)
   - 양자화 버전 사용 가능 (메모리 절약)

동작 방식:
- 원문은 original_content 필드에 저장
- content 필드는 번역된 한국어로 교체
"""
import os
import django
import sys
import time
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review
from django.db.models import Q
import requests

# 번역 방법 선택
TRANSLATION_METHOD = 'googletrans'  # 'googletrans', 'papago', 'google_api', 'mbart'


def detect_language(text):
    """텍스트 언어 감지 (간단한 휴리스틱)"""
    # 한글이 포함되어 있으면 한국어로 간주
    if re.search(r'[가-힣]', text):
        return 'ko'
    
    # 영어로 간주
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    
    return 'unknown'


def translate_with_googletrans(text, target_lang='ko'):
    """deep-translator 라이브러리 사용 (무료, googletrans 대체)"""
    try:
        from deep_translator import GoogleTranslator
        
        # GoogleTranslator는 자동으로 언어를 감지하고 번역합니다
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        # 텍스트가 너무 길면 분할해서 번역 (5000자 제한)
        max_length = 5000
        if len(text) > max_length:
            # 긴 텍스트는 여러 부분으로 나눠서 번역
            parts = []
            for i in range(0, len(text), max_length):
                part = text[i:i + max_length]
                translated_part = translator.translate(part)
                parts.append(translated_part)
            return ' '.join(parts)
        else:
            translated = translator.translate(text)
            return translated
        
    except ImportError:
        print("deep-translator가 설치되지 않았습니다.")
        print("설치: pip install deep-translator>=1.11.0")
        return None
    except Exception as e:
        print(f"번역 실패: {str(e)}")
        return None


def translate_with_papago(text, client_id, client_secret):
    """
    네이버 Papago API 사용 (한국어 번역 품질 좋음)
    
    ⚠️ API 제한:
    - 한 번에 최대 5,000자까지 번역 가능
    - 하루 최대 10,000자까지 번역 가능 (무료 플랜)
    - 초당 10개 요청 제한
    """
    # 텍스트 길이 확인
    if len(text) > 5000:
        print(f"  ⚠ 텍스트가 너무 깁니다 ({len(text)}자). 5,000자로 자릅니다.")
        text = text[:5000]
    
    url = "https://openapi.naver.com/v1/papago/n2mt"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    data = {
        "source": "en",
        "target": "ko",
        "text": text
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result['message']['result']['translatedText']
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"  ⚠ Papago API 일일 할당량 초과 (하루 10,000자 제한)")
        else:
            print(f"  ⚠ Papago 번역 실패: HTTP {e.response.status_code}")
        return None
    except Exception as e:
        print(f"  ⚠ Papago 번역 실패: {str(e)}")
        return None


def translate_with_google_api(text, api_key):
    """
    Google Cloud Translation API 사용
    
    가격:
    - 월 50만자: 무료
    - 초과분: 100만자당 $20
    """
    url = "https://translation.googleapis.com/language/translate/v2"
    
    params = {
        'key': api_key,
        'q': text,
        'source': 'en',
        'target': 'ko',
        'format': 'text'
    }
    
    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result['data']['translations'][0]['translatedText']
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"  ⚠ API 키 인증 실패 또는 할당량 초과")
        elif e.response.status_code == 400:
            print(f"  ⚠ 잘못된 요청: {e.response.text}")
        else:
            print(f"  ⚠ HTTP 에러 {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        print(f"  ⚠ Google API 번역 실패: {str(e)}")
        return None


def translate_with_mbart(text, use_gpu=True, use_quantized=False):
    """
    Facebook mbart-large-50-many-to-many-mmt 모델 사용
    
    GPU 요구사항:
    - 권장: GPU (약 6-8GB VRAM)
    - CPU에서도 실행 가능 (느림)
    - 양자화 버전 사용 시 메모리 절약 가능
    """
    try:
        from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
        import torch
        
        # GPU 사용 가능 여부 확인
        device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        
        if use_quantized:
            # 양자화 버전 사용 (메모리 절약)
            model_name = "RichardErkhov/facebook_-_mbart-large-50-many-to-many-mmt-4bits"
            print(f"  [INFO] 양자화 버전 사용: {model_name}")
        else:
            model_name = "facebook/mbart-large-50-many-to-many-mmt"
        
        # 모델과 토크나이저 로드 (한 번만 로드)
        if not hasattr(translate_with_mbart, 'tokenizer'):
            print(f"  [INFO] 모델 로딩 중: {model_name}")
            print(f"  [INFO] 디바이스: {device}")
            translate_with_mbart.tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
            translate_with_mbart.model = MBartForConditionalGeneration.from_pretrained(model_name)
            translate_with_mbart.model = translate_with_mbart.model.to(device)
            translate_with_mbart.model.eval()
            print(f"  [INFO] 모델 로딩 완료")
        
        tokenizer = translate_with_mbart.tokenizer
        model = translate_with_mbart.model
        
        # 언어 코드 설정 (영어 -> 한국어)
        tokenizer.src_lang = "en_XX"
        
        # 텍스트 인코딩
        encoded = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        
        # 번역 생성
        with torch.no_grad():
            generated_tokens = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.lang_code_to_id["ko_KR"]
            )
        
        # 디코딩
        translated = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        return translated
        
    except ImportError:
        print("  [ERROR] transformers와 torch가 설치되지 않았습니다.")
        print("  설치: pip install transformers torch")
        return None
    except Exception as e:
        print(f"  [ERROR] mbart 번역 실패: {str(e)}")
        return None


def translate_review(review, method='googletrans', **kwargs):
    """리뷰 번역"""
    content = review.content
    
    # 이미 한국어인지 확인
    if detect_language(content) == 'ko':
        return None, 'already_korean'
    
    # 번역 실행
    if method == 'googletrans':
        translated = translate_with_googletrans(content, 'ko')
    elif method == 'papago':
        translated = translate_with_papago(
            content, 
            kwargs.get('client_id'), 
            kwargs.get('client_secret')
        )
    elif method == 'google_api':
        translated = translate_with_google_api(content, kwargs.get('api_key'))
    elif method == 'mbart':
        translated = translate_with_mbart(
            content,
            use_gpu=kwargs.get('use_gpu', True),
            use_quantized=kwargs.get('use_quantized', False)
        )
    else:
        return None, 'unknown_method'
    
    if translated:
        return translated, 'success'
    else:
        return None, 'failed'


def translate_all_reviews(method='googletrans', max_reviews=None, update_content=True, max_chars=500000, **kwargs):
    """
    모든 영어 리뷰를 한국어로 번역
    
    Args:
        max_chars: 최대 번역할 글자 수 (기본값: 500,000자 - Google API 무료 할당량)
    """
    print("=" * 60)
    print("리뷰 번역 시작")
    print(f"번역 방법: {method}")
    if method == 'papago':
        print("[WARNING] Papago API 제한: 한 번에 최대 5,000자, 하루 최대 10,000자")
    elif method == 'google_api':
        print(f"[INFO] Google Translate API 사용")
        print(f"[INFO] 최대 번역 글자 수: {max_chars:,}자 (무료 할당량)")
    elif method == 'mbart':
        print(f"[INFO] mbart-large-50 모델 사용")
        if kwargs.get('use_gpu', True):
            print(f"[INFO] GPU 사용 (권장)")
        else:
            print(f"[INFO] CPU 사용 (느림)")
        if kwargs.get('use_quantized', False):
            print(f"[INFO] 양자화 버전 사용 (메모리 절약)")
    print("=" * 60)
    
    # 영어 리뷰 찾기 (한글이 없는 리뷰)
    reviews = Review.objects.all()
    
    # 한글이 없는 리뷰 필터링
    english_reviews = []
    for review in reviews:
        if detect_language(review.content) == 'en':
            english_reviews.append(review)
    
    if max_reviews:
        english_reviews = english_reviews[:max_reviews]
    
    total = len(english_reviews)
    print(f"\n총 {total}개 영어 리뷰 발견\n")
    
    if total == 0:
        print("번역할 리뷰가 없습니다.")
        return
    
    translated_count = 0
    failed_count = 0
    already_korean_count = 0
    total_chars_translated = 0
    
    for idx, review in enumerate(english_reviews, 1):
        try:
            review_length = len(review.content)
            
            # 글자 수 제한 확인
            if total_chars_translated + review_length > max_chars:
                remaining = max_chars - total_chars_translated
                print(f"\n[STOP] 글자 수 제한 도달!")
                print(f"  번역된 글자 수: {total_chars_translated:,}자")
                print(f"  남은 할당량: {remaining:,}자")
                print(f"  다음 리뷰 길이: {review_length}자 (제한 초과)")
                break
            
            print(f"[{idx}/{total}] 리뷰 ID {review.id} 번역 중... ({review_length}자)")
            print(f"  원문: {review.content[:100]}...")
            
            translated, status = translate_review(review, method=method, **kwargs)
            
            if status == 'success' and translated:
                if update_content:
                    # 원문을 original_content에 저장하고, content를 번역으로 교체
                    if not review.original_content:  # 원문이 없을 때만 저장
                        review.original_content = review.content
                    review.content = translated
                    review.save()
                    print(f"  [OK] 번역 완료: {translated[:100]}...")
                    total_chars_translated += review_length
                else:
                    # 번역만 출력 (저장 안 함)
                    print(f"  [OK] 번역: {translated[:100]}...")
                    total_chars_translated += review_length
                translated_count += 1
            elif status == 'already_korean':
                already_korean_count += 1
                print(f"  [SKIP] 이미 한국어")
            else:
                failed_count += 1
                print(f"  [FAIL] 번역 실패")
            
            # API rate limit 방지
            if method == 'googletrans':
                time.sleep(0.5)  # deep-translator는 무료지만 제한 있음
            elif method == 'papago':
                # Papago API 제한: 한 번에 최대 5,000자, 하루 최대 10,000자
                # 초당 10개 요청 제한
                time.sleep(0.1)
            elif method == 'google_api':
                time.sleep(0.1)  # Google API는 초당 100개 요청 가능
            elif method == 'mbart':
                # mbart는 로컬 모델이므로 딜레이 불필요 (처리 시간이 오래 걸림)
                pass
            
            if idx % 10 == 0:
                print(f"\n[진행 상황] {idx}/{total} 리뷰 처리")
                print(f"  번역 완료: {translated_count}개")
                print(f"  번역된 글자 수: {total_chars_translated:,}자 / {max_chars:,}자")
                print(f"  남은 할당량: {max_chars - total_chars_translated:,}자\n")
                
        except Exception as e:
            print(f"  [ERROR] 에러: {str(e)}")
            failed_count += 1
            continue
    
    print("\n" + "=" * 60)
    print("번역 완료!")
    print(f"  - 번역 성공: {translated_count}개")
    print(f"  - 번역 실패: {failed_count}개")
    print(f"  - 이미 한국어: {already_korean_count}개")
    print(f"  - 총 번역된 글자 수: {total_chars_translated:,}자")
    if method == 'google_api':
        remaining_quota = max_chars - total_chars_translated
        print(f"  - 남은 무료 할당량: {remaining_quota:,}자")
    print("=" * 60)


def translate_reviews_by_movie(movie_id, method='googletrans', **kwargs):
    """특정 영화의 리뷰만 번역"""
    from movies.models import Movie
    
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        print(f"영화 ID {movie_id}를 찾을 수 없습니다.")
        return
    
    reviews = Review.objects.filter(movie=movie)
    english_reviews = [r for r in reviews if detect_language(r.content) == 'en']
    
    print(f"\n[{movie.title}] 영어 리뷰 {len(english_reviews)}개 번역 시작\n")
    
    for idx, review in enumerate(english_reviews, 1):
        translated, status = translate_review(review, method=method, **kwargs)
        if status == 'success' and translated:
            # 원문을 original_content에 저장하고, content를 번역으로 교체
            if not review.original_content:
                review.original_content = review.content
            review.content = translated
            review.save()
            print(f"  [{idx}] ✓ 번역 완료")
        else:
            print(f"  [{idx}] ✗ 번역 실패")
        
        time.sleep(0.5)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='리뷰 번역')
    parser.add_argument('--method', choices=['googletrans', 'papago', 'google_api', 'mbart'], 
                        default='googletrans', help='번역 방법')
    parser.add_argument('--use-gpu', action='store_true', default=True,
                        help='mbart 사용 시 GPU 사용 (기본값: True)')
    parser.add_argument('--use-cpu', action='store_true',
                        help='mbart 사용 시 CPU 사용 (GPU 비활성화)')
    parser.add_argument('--use-quantized', action='store_true',
                        help='mbart 양자화 버전 사용 (메모리 절약)')
    parser.add_argument('--max-reviews', type=int, default=None,
                        help='최대 번역할 리뷰 수')
    parser.add_argument('--movie-id', type=int, default=None,
                        help='특정 영화의 리뷰만 번역')
    parser.add_argument('--dry-run', action='store_true',
                        help='번역만 하고 저장하지 않음')
    parser.add_argument('--papago-id', type=str, default=None,
                        help='Papago Client ID')
    parser.add_argument('--papago-secret', type=str, default=None,
                        help='Papago Client Secret')
    parser.add_argument('--google-api-key', type=str, default=None,
                        help='Google Translate API Key')
    parser.add_argument('--max-chars', type=int, default=500000,
                        help='최대 번역할 글자 수 (기본값: 500,000자 - Google API 무료 할당량)')
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.method == 'papago':
        if not args.papago_id or not args.papago_secret:
            print("Papago API를 사용하려면 --papago-id와 --papago-secret이 필요합니다.")
            sys.exit(1)
        kwargs['client_id'] = args.papago_id
        kwargs['client_secret'] = args.papago_secret
    elif args.method == 'google_api':
        if not args.google_api_key:
            print("Google Translate API를 사용하려면 --google-api-key가 필요합니다.")
            sys.exit(1)
        kwargs['api_key'] = args.google_api_key
    elif args.method == 'mbart':
        kwargs['use_gpu'] = not args.use_cpu  # --use-cpu가 있으면 False
        kwargs['use_quantized'] = args.use_quantized
    
    if args.movie_id:
        translate_reviews_by_movie(
            args.movie_id,
            method=args.method,
            **kwargs
        )
    else:
        translate_all_reviews(
            method=args.method,
            max_reviews=args.max_reviews,
            update_content=not args.dry_run,
            max_chars=args.max_chars,
            **kwargs
        )

