# 리뷰 데이터 Fixture (테스트용)

## 개요

이 디렉토리에는 테스트 목적으로 사용할 수 있는 샘플 리뷰 데이터가 포함되어 있습니다.

## 파일 설명

- `reviews_sample.json`: 전체 리뷰 데이터 (1,211개 리뷰 + 좋아요)

## 데이터 로드 방법

### 사전 요구사항

리뷰를 로드하기 전에 다음 데이터가 있어야 합니다:

1. **영화 데이터** (필수)
   ```bash
   python manage.py loaddata movies/fixtures/movies_initial.json
   ```

2. **사용자 데이터** (필수)
   - 리뷰는 사용자와 연결되어 있으므로 사용자 데이터가 필요합니다.
   - 테스트용 사용자는 `load_data.py test-data` 명령으로 생성할 수 있습니다.

### 리뷰 데이터 로드

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

python manage.py loaddata reviews/fixtures/reviews_sample.json
```

### 전체 테스트 데이터 로드 순서

```bash
# 1. 마이그레이션
python manage.py migrate

# 2. 영화 데이터
python manage.py loaddata movies/fixtures/movies_initial.json

# 3. 테스트 사용자 생성 (선택적)
python load_data.py test-data 5 10  # 5명 사용자, 각 10개 리뷰

# 4. 리뷰 데이터 (기존 리뷰가 있는 경우)
python manage.py loaddata reviews/fixtures/reviews_sample.json
```

## Fixture 생성 방법

새로운 리뷰 fixture를 생성하려면:

```bash
python create_reviews_fixture.py
```

이 스크립트는:
- 모든 리뷰 데이터를 포함
- 모든 리뷰 좋아요 데이터 포함
- `reviews/fixtures/reviews_sample.json` 파일로 저장

## 주의사항

1. **의존성**: 리뷰는 사용자와 영화에 의존하므로, 이들이 먼저 로드되어야 합니다.

2. **중복 방지**: 같은 사용자가 같은 영화에 리뷰를 작성할 수 없습니다 (`unique_together` 제약).

3. **평점 자동 업데이트**: 리뷰가 로드되면 영화의 평균 평점이 자동으로 업데이트됩니다.

4. **테스트 목적**: 이 fixture는 테스트/데모 목적으로만 사용하세요. 실제 운영 환경에서는 사용자가 직접 리뷰를 작성합니다.

## 데이터 통계

- **리뷰 수**: 1,211개 (전체)
- **리뷰 좋아요**: 포함됨
- **파일 크기**: 약 3.1MB
- **데이터 소스**: 기존 DB의 모든 리뷰 데이터

## 문제 해결

### 오류: "User matching query does not exist"
- 사용자 데이터가 먼저 로드되어야 합니다.
- `load_data.py test-data` 명령으로 테스트 사용자를 생성하세요.

### 오류: "Movie matching query does not exist"
- 영화 데이터가 먼저 로드되어야 합니다.
- `python manage.py loaddata movies/fixtures/movies_initial.json` 실행

### 중복 리뷰 오류
- 같은 사용자가 같은 영화에 리뷰를 작성하려고 하면 오류가 발생합니다.
- Fixture에서 중복을 제거하거나, 기존 리뷰를 삭제한 후 다시 로드하세요.

