# ChromaDB 벡터 데이터베이스 가이드

## 개요

리뷰 임베딩 데이터를 ChromaDB 벡터 데이터베이스에 저장하여 유사도 검색을 수행할 수 있습니다.

## 설치

필요한 패키지는 이미 `requirements.txt`에 포함되어 있습니다:

```bash
pip install -r requirements.txt
```

## ChromaDB 생성

### 1. Parquet 파일에서 ChromaDB 생성

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

python create_chroma_db.py
```

### 2. 옵션 설정

```bash
# 커스텀 경로 및 컬렉션 이름 지정
python create_chroma_db.py \
    --parquet review_embeddings_final.parquet \
    --db-path ./chroma_db \
    --collection review_embeddings
```

## 사용 방법

### Django에서 ChromaDB 사용

```python
from reviews.chroma_utils import (
    search_similar_reviews,
    get_review_by_id,
    get_collection_stats
)

# 1. 유사 리뷰 검색
query_embedding = [...]  # 1024차원 임베딩 벡터
results = search_similar_reviews(
    query_embedding=query_embedding,
    n_results=10,
    movie_id=175,  # 선택: 특정 영화로 필터링
    user_id=8,     # 선택: 특정 사용자로 필터링
    meta_class="RICH"  # 선택: 메타 클래스로 필터링
)

for result in results:
    print(f"리뷰 ID: {result['review_id']}")
    print(f"거리: {result['distance']}")
    print(f"내용: {result['document']}")
    print(f"메타데이터: {result['metadata']}")

# 2. 특정 리뷰 조회
review = get_review_by_id(104)
if review:
    print(review['metadata'])
    print(review['document'])

# 3. 컬렉션 통계
stats = get_collection_stats()
print(f"총 리뷰 수: {stats['total_reviews']}")
```

## 데이터 구조

### Parquet 파일 구조

- `id`: 리뷰 ID
- `movie_id`: 영화 ID
- `user_id`: 사용자 ID
- `processed_text`: 처리된 리뷰 텍스트
- `keywords`: 키워드 배열
- `embedding_vector`: 1024차원 임베딩 벡터
- `meta_class`: 메타 클래스 (예: RICH)

### ChromaDB 저장 구조

- **ID**: 리뷰 ID (문자열)
- **Embedding**: 1024차원 벡터
- **Document**: 처리된 리뷰 텍스트
- **Metadata**:
  - `review_id`: 리뷰 ID
  - `movie_id`: 영화 ID
  - `user_id`: 사용자 ID
  - `meta_class`: 메타 클래스
  - `keywords`: 키워드 (쉼표로 구분)

## 테스트

```bash
python test_chroma_search.py
```

## 파일 위치

- **ChromaDB 저장 경로**: `django-project/chroma_db/`
- **유틸리티 모듈**: `django-project/reviews/chroma_utils.py`
- **생성 스크립트**: `django-project/create_chroma_db.py`
- **테스트 스크립트**: `django-project/test_chroma_search.py`

## 주의사항

1. **임베딩 차원**: 현재 임베딩 벡터는 1024차원입니다. 다른 차원의 임베딩을 사용하려면 ChromaDB 컬렉션을 재생성해야 합니다.

2. **검색 성능**: 대량의 데이터에서 검색할 때는 `n_results`를 적절히 조정하세요.

3. **필터링**: `movie_id`, `user_id`, `meta_class`로 필터링할 수 있지만, 필터 조건이 너무 많으면 검색 결과가 없을 수 있습니다.

4. **데이터 업데이트**: 새로운 리뷰 임베딩을 추가하려면 `create_chroma_db.py`를 다시 실행하거나 ChromaDB API를 직접 사용해야 합니다.

## 문제 해결

### 컬렉션을 찾을 수 없음

```python
# 컬렉션이 없으면 먼저 생성해야 합니다
python create_chroma_db.py
```

### 임베딩 차원 오류

임베딩 벡터의 차원이 1024가 아닌 경우, ChromaDB 컬렉션을 재생성해야 합니다.

### 검색 결과가 없음

- 필터 조건이 너무 엄격한지 확인
- `n_results` 값을 늘려보세요
- 쿼리 임베딩 벡터가 올바른지 확인

