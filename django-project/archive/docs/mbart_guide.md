# mbart-large-50 모델 사용 가이드

## 모델 정보

- **모델명**: facebook/mbart-large-50-many-to-many-mmt
- **파라미터**: 6억 개 이상
- **용도**: 다국어 기계 번역 (50개 언어 지원)

## GPU 요구사항

### 권장 사양
- **GPU**: NVIDIA GPU (CUDA 지원)
- **VRAM**: 약 6-8GB
- **예시**: GTX 1060 6GB, RTX 3060, RTX 2060 등

### CPU 사용
- GPU가 없어도 CPU에서 실행 가능
- **단점**: 매우 느림 (GPU 대비 10-50배 느림)
- **장점**: 추가 하드웨어 불필요

## 설치 방법

```bash
# 기본 설치
pip install transformers torch

# GPU 사용 시 (CUDA 지원)
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CPU만 사용 시
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu
```

## 사용 방법

### GPU 사용 (권장)
```bash
python translate_reviews.py --method mbart --use-gpu
```

### CPU 사용
```bash
python translate_reviews.py --method mbart --use-cpu
```

### 양자화 버전 사용 (메모리 절약)
```bash
python translate_reviews.py --method mbart --use-quantized
```

## 성능 비교

- **GPU (RTX 3060)**: 약 1-2초/리뷰
- **CPU (i7)**: 약 10-30초/리뷰
- **양자화 버전**: 메모리 50% 절약, 속도 약간 느림

## 메모리 사용량

- **일반 버전**: 약 2.5GB (GPU VRAM)
- **양자화 버전**: 약 1.2GB (GPU VRAM)
- **CPU**: 약 4-6GB (RAM)

## 장단점

### 장점
- ✅ 완전 무료 (오프라인)
- ✅ API 제한 없음
- ✅ 번역 품질 좋음
- ✅ 50개 언어 지원

### 단점
- ❌ 초기 모델 다운로드 시간 (약 2-3GB)
- ❌ GPU 없으면 매우 느림
- ❌ 메모리 사용량 많음

## 대안

GPU가 없거나 메모리가 부족한 경우:
1. **양자화 버전 사용**: `--use-quantized`
2. **Google Colab 사용**: 무료 GPU 제공
3. **googletrans 사용**: 더 가볍고 빠름

