# 검색 결과 문제 해결 가이드

## 발견된 문제

1. **임베딩 모델 불일치**
   - Parquet 파일의 임베딩: 원본 모델로 생성 (1024차원, 정규화됨)
   - 현재 검색 모델: `paraphrase-multilingual-MiniLM-L12-v2` (384차원 → 1024 패딩)
   - 결과: 유사도 계산이 부정확함

2. **패딩 문제**
   - 384차원 임베딩을 0으로 패딩하여 1024차원으로 확장
   - 패딩된 0 값들이 유사도 계산에 부정확한 영향을 줌

3. **유사도가 낮음**
   - 현재 유사도: 0.5~0.53 정도
   - 이전 임계값 0.9는 너무 높아서 항상 의미 모드로 동작

## 해결 방법

### 방법 1: 원본 모델 사용 (권장)

Parquet 파일을 생성한 모델과 동일한 모델을 사용해야 합니다.

```bash
# 원본 모델 확인 필요
# parquet 파일 생성 시 사용한 모델 확인
```

### 방법 2: 임계값 조정 (현재 적용)

- `SIMILARITY_THRESHOLD`를 0.9 → 0.7로 낮춤
- 낮은 유사도에서도 키워드 모드로 판단 가능

### 방법 3: 패딩 대신 차원 축소

1024차원 임베딩을 384차원으로 축소하는 방법:

```python
# PCA 또는 선형 변환 사용
from sklearn.decomposition import PCA

# 1024차원 → 384차원 축소
pca = PCA(n_components=384)
reduced_embedding = pca.fit_transform(original_embedding)
```

### 방법 4: ChromaDB 재생성

원본 모델로 검색어를 임베딩하여 ChromaDB를 재생성:

```python
# 원본 모델 사용
model = SentenceTransformer("원본_모델_이름")
embeddings = model.encode(texts, normalize_embeddings=True)
```

## 현재 상태

- ✅ 거리 값 정상화 (0.9~1.0 범위)
- ✅ 임계값 조정 (0.9 → 0.7)
- ⚠️ 유사도가 여전히 낮음 (0.5~0.53)
- ⚠️ 검색 결과 정확도 개선 필요

## 권장 사항

1. **단기**: 임계값을 더 낮추거나 가중치 조정
2. **중기**: 원본 parquet 파일 생성 모델 확인 및 동일 모델 사용
3. **장기**: 원본 모델로 ChromaDB 재생성

## 디버깅

```bash
python test_search_debug.py
```

이 스크립트로 검색 결과와 유사도를 확인할 수 있습니다.

