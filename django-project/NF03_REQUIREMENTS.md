# NF03 요구사항: 영화 데이터 확보

## 요구사항 번호
**NF03**

## 요구사항 내용
서비스의 원활한 운영을 위한 양질의 데이터를 확보할 수 있도록 한다.

## 구현 내용

### ✅ 1. 최소 50개의 영화 정보 데이터
- **현재 상태**: **200개 영화** 보유 (요구사항 초과 달성)
- **데이터 소스**: TMDB (The Movie Database) API
- **데이터 형식**: Django Model (Movie, Genre)

### ✅ 2. Load 가능한 Fixture 형태
- **영화 데이터 Fixture**:
  - **위치**: `movies/fixtures/movies_initial.json`
  - **포함 데이터**:
    - 영화 정보 (200개)
    - 장르 정보 (약 20개)
  - **로드 방법**:
    ```bash
    python manage.py loaddata movies/fixtures/movies_initial.json
    ```

- **리뷰 데이터 Fixture (테스트용)**:
  - **위치**: `reviews/fixtures/reviews_sample.json`
  - **포함 데이터**:
    - 전체 리뷰 (1,211개)
    - 리뷰 좋아요 데이터
  - **파일 크기**: 약 3.1MB
  - **생성 방법**:
    ```bash
    python create_reviews_fixture.py
    ```
  - **로드 방법**:
    ```bash
    python manage.py loaddata reviews/fixtures/reviews_sample.json
    ```
  - **주의**: 영화와 사용자 데이터가 먼저 로드되어야 함

### ✅ 3. 주기적 업데이트 기능
- **스크립트**: `load_data.py`
- **기능**:
  - `update-empty`: 설명이 비어있는 영화만 업데이트
  - `update-all`: 모든 영화 설명 업데이트
  - `movies [페이지수]`: 새로운 영화 데이터 추가 로드

### ✅ 4. 데이터 형식 표준화
- **표준화된 속성**:
  - `title`: 한국어 제목
  - `original_title`: 영어 원제
  - `description`: 영어 설명 (AI embedding용)
  - `kor_description`: 한국어 설명 (UI 표시용)
  - `poster_url`: 포스터 이미지 URL
  - `release_year`: 개봉 연도
  - `runtime`: 상영 시간 (분)
  - `director`: 감독
  - `cast`: 출연진 (쉼표로 구분)
  - `heaviness`: 무게감 점수 (0-100)
  - `satisfaction`: 대중성 점수 (0-100)
  - `genres`: 장르 (ManyToMany 관계)

- **TMDB API → 표준 형식 변환**:
  - `overview` → `description` (영어), `kor_description` (한국어)
  - `original_title` → `original_title`
  - `title` (ko-KR) → `title`
  - `poster_path` → `poster_url` (전체 URL로 변환)
  - `release_date` → `release_year` (연도만 추출)
  - `credits.crew` (Director) → `director`
  - `credits.cast` (상위 5명) → `cast`

### ✅ 5. 이용 허락 조건 확인
- **문서**: `TMDB_API_LICENSE.md`
- **주요 내용**:
  - TMDB API는 무료로 제공 (비상업적/교육 목적)
  - TMDB 크레딧 표시 필요
  - Rate Limiting 준수 (초당 40개 요청)
  - 이미지 직접 저장 금지 (URL 참조만)
  - Creative Commons Attribution-ShareAlike 4.0 라이선스

## 데이터 수집 프로세스

### 초기 데이터 로드
```bash
# 1. Fixture로 로드 (빠름)
python manage.py loaddata movies/fixtures/movies_initial.json

# 2. 또는 TMDB API로 직접 로드
python load_data.py
```

### 데이터 업데이트
```bash
# 설명이 비어있는 영화만 업데이트
python load_data.py update-empty

# 모든 영화 정보 업데이트
python load_data.py update-all

# 새로운 영화 추가 (10페이지)
python load_data.py movies 10
```

## 데이터 통계

| 항목 | 수량 | 비고 |
|------|------|------|
| 영화 수 | 200개 | 요구사항: 최소 50개 ✅ |
| 장르 수 | 약 20개 | TMDB 표준 장르 |
| 리뷰 수 | 1,211개 | 테스트용 fixture 포함 |
| 데이터 소스 | TMDB API | The Movie Database |
| 업데이트 기능 | ✅ | 주기적 업데이트 가능 |

## 관련 파일

- `movies/fixtures/movies_initial.json`: Fixture 파일
- `load_data.py`: 데이터 로드/업데이트 스크립트
- `movies/models.py`: Movie, Genre 모델 정의
- `TMDB_API_LICENSE.md`: TMDB API 이용 허락 조건
- `movies/fixtures/README.md`: Fixture 사용 가이드

## 검증 방법

### 1. Fixture 로드 테스트
```bash
# 빈 데이터베이스에서 테스트
python manage.py flush
python manage.py migrate
python manage.py loaddata movies/fixtures/movies_initial.json

# 데이터 확인
python manage.py shell
>>> from movies.models import Movie
>>> Movie.objects.count()  # 200개여야 함
```

### 2. 데이터 업데이트 테스트
```bash
python load_data.py update-empty
```

## 향후 개선 사항

1. **자동화된 주기적 업데이트**
   - Cron job 또는 Celery를 사용한 자동 업데이트 스케줄링

2. **다양한 데이터 소스 통합**
   - 다른 영화 API와의 통합 (필요 시)

3. **데이터 품질 관리**
   - 데이터 검증 로직 추가
   - 중복 데이터 방지 강화

