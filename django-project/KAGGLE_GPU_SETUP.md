# Kaggle GPU 활성화 가이드

## 방법 1: 새 Notebook 생성 시 GPU 활성화

1. [Kaggle.com](https://www.kaggle.com) 로그인
2. 상단 메뉴에서 **"Notebooks"** 클릭
3. 오른쪽 상단의 **"New Notebook"** 버튼 클릭
4. Notebook 생성 후:
   - 오른쪽 상단의 **"Settings"** (톱니바퀴 아이콘) 클릭
   - **"Accelerator"** 섹션 찾기
   - **"GPU"** 선택 (T4 GPU가 기본 제공됨)
   - **"Save"** 클릭

## 방법 2: 기존 Notebook에서 GPU 활성화

1. Notebook 편집 모드로 들어가기
2. 오른쪽 상단의 **"Settings"** (톱니바퀴 아이콘) 클릭
3. **"Accelerator"** 섹션에서:
   - **"None"** → **"GPU"**로 변경
   - **"Save"** 클릭
4. **주의**: GPU 활성화 시 Notebook이 재시작될 수 있음

## GPU 확인 방법

Notebook 셀에서 다음 코드 실행:

```python
import torch

# GPU 사용 가능 여부 확인
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
print(f"GPU 개수: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU 이름: {torch.cuda.get_device_name(0)}")
    print(f"GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

**예상 출력**:
```
CUDA 사용 가능: True
GPU 개수: 1
GPU 이름: Tesla T4
GPU 메모리: 15.00 GB
```

## GPU 제한사항

- **무료 계정**: 주당 30시간 GPU 사용 가능
- **세션 시간**: 최대 9시간 (자동 종료)
- **GPU 타입**: 주로 Tesla T4 (16GB VRAM)

## GPU 사용량 확인

```python
import torch

if torch.cuda.is_available():
    print(f"현재 GPU 메모리 사용량: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"최대 GPU 메모리 사용량: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")
```

## 문제 해결

### GPU가 활성화되지 않는 경우

1. **Settings 확인**: Accelerator가 "GPU"로 설정되어 있는지 확인
2. **Notebook 재시작**: Settings 저장 후 Notebook 재시작
3. **인터넷 활성화**: Settings → Internet → "On"으로 설정
4. **할당량 확인**: 주당 30시간 제한 확인

### GPU 메모리 부족 오류

```python
# 양자화 버전 사용 (메모리 절약)
use_quantized = True  # kaggle_translate_reviews.py에서 설정
```

또는 배치 크기 줄이기

## 번역 스크립트 실행 전 체크리스트

- [ ] GPU 활성화됨 (Settings → Accelerator → GPU)
- [ ] 인터넷 활성화됨 (Settings → Internet → On)
- [ ] Dataset 추가됨 (reviews_input_part*.json 파일들)
- [ ] 필요한 라이브러리 설치: `!pip install transformers torch tqdm`

## 예상 성능

- **Kaggle T4 GPU**: 약 30분~1시간 (1,104개 리뷰)
- **CPU**: 약 3-9시간 (비추천)

