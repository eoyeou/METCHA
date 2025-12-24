# 임베딩 모델 옵션 가이드

## 현재 사용 중인 모델

**기본값**: `BAAI/bge-m3` (원본 parquet 파일 생성 모델)
- 크기: ~2.27GB
- 차원: 1024차원 (원본과 동일)
- 다국어 지원: ✅ (한국어 성능 우수)
- 속도: 보통 (GPU 권장)
- 성능: 우수
- 정규화: normalize_embeddings=True (코사인 유사도 최적화)

## 가벼운 모델 옵션

### 1. all-MiniLM-L6-v2 (가장 가벼움) ⭐ 추천
```python
# 환경 변수 설정
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```
- 크기: ~80MB
- 차원: 384차원
- 다국어 지원: ❌ (영어 전용)
- 속도: 매우 빠름
- 성능: 양호 (영어만)
- **주의**: 한국어 검색 시 성능 저하 가능

### 2. paraphrase-multilingual-MiniLM-L12-v2 (현재 기본값)
```python
# 환경 변수 설정 (또는 기본값)
export EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```
- 크기: ~420MB
- 차원: 384차원
- 다국어 지원: ✅
- 속도: 빠름
- 성능: 양호

### 3. paraphrase-MiniLM-L3-v2 (초경량)
```python
export EMBEDDING_MODEL="sentence-transformers/paraphrase-MiniLM-L3-v2"
```
- 크기: ~60MB
- 차원: 384차원
- 다국어 지원: ❌ (영어 전용)
- 속도: 매우 빠름
- 성능: 보통

## 무거운 모델 옵션 (더 정확하지만 느림)

### 4. paraphrase-multilingual-mpnet-base-v2 (이전 사용 모델)
```python
export EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
```
- 크기: ~1.1GB
- 차원: 768차원
- 다국어 지원: ✅
- 속도: 느림
- 성능: 우수

## 한국어 특화 모델

### 5. jhgan/ko-sroberta-multitask
```python
export EMBEDDING_MODEL="jhgan/ko-sroberta-multitask"
```
- 크기: ~500MB
- 차원: 768차원
- 다국어 지원: 한국어 특화
- 속도: 보통
- 성능: 한국어에 최적화

## 모델 변경 방법

### 방법 1: 환경 변수 설정 (권장)
```bash
# Windows (PowerShell)
$env:EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Windows (CMD)
set EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Linux/Mac
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

### 방법 2: 코드에서 직접 수정
`reviews/embedding_utils.py` 파일의 `model_name` 변수 수정

## 성능 비교

| 모델 | 크기 | 속도 | 한국어 지원 | 정확도 |
|------|------|------|------------|--------|
| all-MiniLM-L6-v2 | 80MB | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ |
| paraphrase-MiniLM-L3-v2 | 60MB | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ |
| paraphrase-multilingual-MiniLM-L12-v2 | 420MB | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ |
| paraphrase-multilingual-mpnet-base-v2 | 1.1GB | ⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| jhgan/ko-sroberta-multitask | 500MB | ⭐⭐⭐ | ✅ (한국어 최적) | ⭐⭐⭐⭐ |

## 추천

- **한국어 검색이 중요**: `paraphrase-multilingual-MiniLM-L12-v2` (현재 기본값)
- **영어만 사용 + 최대 속도**: `all-MiniLM-L6-v2`
- **최고 정확도 필요**: `paraphrase-multilingual-mpnet-base-v2`

## 주의사항

1. **차원 불일치**: 가벼운 모델들은 384차원을 생성하지만, ChromaDB는 1024차원을 기대합니다.
   - 현재 구현은 자동으로 패딩하여 1024차원으로 확장합니다.
   - 성능 저하가 있을 수 있으므로, 가능하면 원본 parquet 파일 생성 모델과 동일한 모델 사용을 권장합니다.

2. **첫 로딩 시간**: 모델을 처음 로드할 때 다운로드 시간이 소요됩니다.
   - 이후에는 캐시된 모델을 사용하므로 빠릅니다.

3. **메모리 사용량**: 모델 크기와 비례하여 메모리를 사용합니다.

