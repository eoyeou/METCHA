# Kaggle에서 리뷰 번역하기 가이드

## 전체 프로세스

1. **로컬**: 영어 리뷰 추출 → `reviews_input.json` 생성
2. **Kaggle**: 번역 수행 → `reviews_translated.json` 생성
3. **로컬**: 번역 결과 DB 반영

---

## 1단계: 로컬에서 영어 리뷰 추출

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

python export_reviews_for_kaggle.py
```

**결과**: `reviews_input.json` 파일 생성

**파일 형식**:
```json
[
    {
        "id": 1,
        "content": "This movie is great!",
        "movie_id": 123,
        "user_id": 456,
        "rating": 4.5
    },
    ...
]
```

---

## 2단계: Kaggle에서 번역 수행

### 2-1. Kaggle Notebook 생성

1. [Kaggle.com](https://www.kaggle.com) 로그인
2. "Notebooks" → "New Notebook" 클릭
3. Settings → Accelerator → **GPU** 선택 (중요!)

### 2-2. 파일 업로드 (두 가지 방법)

**방법 A: Kaggle Dataset 사용 (권장)**
1. Kaggle → Datasets → New Dataset 클릭
2. `reviews_input_part01.json`과 `reviews_input_part02.json` 모두 업로드
3. Notebook에서 "Add Data" → 방금 만든 Dataset 선택

**방법 B: 코드에 직접 포함**
- Notebook 셀에서 JSON 데이터를 직접 생성하거나
- 로컬에서 생성한 JSON 파일 내용을 코드에 포함

### 2-3. 스크립트 실행

Kaggle Notebook에 다음 코드 입력:

```python
# 필요한 라이브러리 설치
!pip install transformers torch tqdm

# 스크립트 파일 업로드 (또는 직접 코드 복사)
# kaggle_translate_reviews.py 내용을 셀에 붙여넣기

# 또는 파일로 업로드한 경우
exec(open('kaggle_translate_reviews.py').read())
```

또는 직접 실행:

```python
import json
import re
import torch
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from tqdm import tqdm
import os

# ... (kaggle_translate_reviews.py의 모든 코드)

# 실행
main()
```

### 2-4. 결과 다운로드

번역 완료 후 다음 파일들을 다운로드:
- `reviews_translated_part01.json`
- `reviews_translated_part02.json`
- (필요시 더 많은 파일)

**예상 시간**: Kaggle T4 GPU 기준 약 30분~1시간

---

## 3단계: 로컬에서 DB 반영

### 3-1. 번역 파일 병합 (여러 파일인 경우)

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

python merge_translated_reviews.py
```

이 명령은 `reviews_translated_part*.json` 파일들을 자동으로 찾아서 `reviews_translated.json`으로 병합합니다.

### 3-2. DB에 반영

```bash
python import_translated_reviews.py reviews_translated.json
```

**동작**:
- `reviews_translated.json` 파일 읽기
- 각 리뷰의 `id`로 DB에서 리뷰 찾기
- `original_content`에 원문 저장
- `content`에 번역문 저장

---

## 파일 구조

```
django-project/
├── export_reviews_for_kaggle.py      # 1단계: 영어 리뷰 추출
├── kaggle_translate_reviews.py       # 2단계: Kaggle 번역 스크립트
├── import_translated_reviews.py      # 3단계: DB 반영
├── merge_translated_reviews.py       # 3-1단계: 번역 파일 병합
├── reviews_input_part01.json         # Kaggle에 업로드할 파일 (1)
├── reviews_input_part02.json         # Kaggle에 업로드할 파일 (2)
├── reviews_translated_part01.json    # Kaggle에서 다운로드한 파일 (1)
├── reviews_translated_part02.json    # Kaggle에서 다운로드한 파일 (2)
└── reviews_translated.json           # 병합된 최종 파일
```

---

## 주의사항

1. **Kaggle GPU 제한**: 주당 30시간 무료 GPU 제공
2. **파일 크기**: 리뷰가 많으면 JSON 파일이 클 수 있음 (수백 MB)
3. **중복 실행 방지**: 이미 번역된 리뷰(`original_content`가 있는 리뷰)는 자동으로 건너뜀
4. **백업**: DB 반영 전에 백업 권장

---

## 문제 해결

### Kaggle에서 모델 다운로드 실패
- 인터넷 연결 확인
- Kaggle Notebook의 인터넷 설정 확인

### 메모리 부족
- `use_quantized=True`로 변경 (양자화 버전 사용)

### 번역 품질이 낮음
- `num_beams` 파라미터 조정 (기본값: 4)
- 더 긴 `max_length` 사용 (기본값: 512)

---

## 예상 시간 및 비용

| 단계 | 시간 | 비용 |
|------|------|------|
| 1단계 (추출) | 1분 | 무료 |
| 2단계 (Kaggle 번역) | 30분~1시간 | 무료 (GPU 할당량 내) |
| 3단계 (DB 반영) | 1분 | 무료 |
| **총계** | **약 1시간** | **무료** |

