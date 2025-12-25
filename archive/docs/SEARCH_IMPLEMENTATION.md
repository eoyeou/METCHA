# 검색 시스템 구현 가이드

## 개요

ChromaDB 기반 의미 검색 시스템이 구현되었습니다. 검색어를 임베딩하여 ChromaDB의 리뷰 임베딩과 유사도를 계산하고, 사용자 취향을 반영한 결과를 제공합니다.

## 검색 프로세스

### 1. 검색어 입력
- 사용자가 검색창에 검색어 입력
- 입력 중 변화가 있을 때마다 실시간으로 검색 수행 (디바운싱 300ms)

### 2. 임베딩 변환
- 검색어를 1024차원 임베딩 벡터로 변환
- `reviews/embedding_utils.py`의 `embed_text()` 함수 사용

### 3. ChromaDB 유사도 검색
- 임베딩 벡터로 ChromaDB에서 유사한 리뷰 검색
- 코사인 거리를 유사도로 변환 (0~1 범위)

### 4. 검색 모드 결정
- **유사도 ≥ 0.9**: 키워드 모드
  - 단순 키워드 매칭으로 판단
  - 유사도 점수만으로 정렬
  
- **유사도 < 0.9**: 의미 모드
  - 특별한 목적 없는 문장으로 판단
  - 유사도 + 사용자 취향 적합도로 정렬

### 5. 사용자 취향 반영 (의미 모드만)
- 사용자가 4~5점 준 영화들의 평균 Heaviness, Satisfaction 계산
- 취향 적합도 계산:
  - `H_fit = 1.0 - (|User_H - Movie_H| / 100)`
  - `S_fit = 1.0 - (|User_S - Movie_S| / 100)`
  - `S_personal = (H_fit + S_fit) / 2`
- 최종 점수: `유사도 * 0.7 + 취향 적합도 * 0.3`

### 6. 결과 반환
- 최종 점수로 정렬된 영화 목록 반환

## 주요 파일

### 백엔드
- `movies/search_views.py`: 검색 API 엔드포인트
- `reviews/embedding_utils.py`: 검색어 임베딩 변환
- `reviews/chroma_utils.py`: ChromaDB 검색 유틸리티
- `accounts/models.py`: User 모델에 취향 점수 필드 추가

### 프론트엔드
- `vue-project/src/views/SearchResultsView.vue`: 검색 결과 페이지
- `vue-project/src/views/HomeView.vue`: 홈 화면 검색창

## API 엔드포인트

### POST `/api/movies/search/semantic/`

**Request:**
```json
{
  "query": "비오는 날 보기 좋은 영화",
  "limit": 20
}
```

**Response:**
```json
{
  "results": [영화 리스트],
  "similarity_mode": "keyword" | "semantic",
  "max_similarity": 0.95,
  "total_found": 15
}
```

## 설정 가능한 파라미터

### `movies/search_views.py`에서 수정 가능:

```python
SIMILARITY_THRESHOLD = 0.9  # 유사도 임계값 (키워드/의미 모드 구분)
SIMILARITY_WEIGHT = 0.7     # 유사도 가중치
PREFERENCE_WEIGHT = 0.3     # 취향 적합도 가중치
```

## 사용자 취향 점수 자동 업데이트

리뷰 생성/수정 시 자동으로 사용자 취향 점수가 업데이트됩니다:
- 4점 이상 평점을 준 영화들의 평균 Heaviness, Satisfaction 계산
- `User.avg_heaviness`, `User.avg_satisfaction` 필드에 저장

## 주의사항

1. **임베딩 모델**: 현재 `paraphrase-multilingual-mpnet-base-v2` 사용 (768차원)
   - 1024차원이 필요하면 패딩으로 확장
   - 실제 parquet 파일 생성 모델과 동일해야 최적 성능

2. **ChromaDB**: 검색 전에 `create_chroma_db.py` 실행 필요

3. **성능**: 첫 검색 시 임베딩 모델 로딩으로 인해 지연 가능 (약 2-3초)

## 테스트

```bash
# 검색 API 테스트
curl -X POST http://127.0.0.1:8000/api/movies/search/semantic/ \
  -H "Content-Type: application/json" \
  -d '{"query": "액션 영화", "limit": 10}'
```

