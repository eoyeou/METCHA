# Fixtures 로드 가이드

## 문제 해결

fixtures 파일들이 데이터베이스에 로드되지 않는 경우, 다음을 확인하세요.

### 1. 가상환경 활성화 필수

가상환경을 활성화하지 않으면 `ModuleNotFoundError: No module named 'environ'` 오류가 발생합니다.

**Windows:**
```bash
cd django-project
source venv/Scripts/activate
```

**Linux/Mac:**
```bash
cd django-project
source venv/bin/activate
```

### 2. 자동 로드 스크립트 사용 (권장)

가장 간단한 방법은 제공된 스크립트를 사용하는 것입니다:

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

# 영화 데이터만 로드
python load_fixtures.py

# 영화 데이터 + 사용자 생성 + 리뷰 데이터 로드
python load_fixtures.py --with-reviews
```

### 3. 수동 로드 방법

#### 영화 데이터 로드

```bash
cd django-project
source venv/Scripts/activate  # Windows
python manage.py loaddata movies/fixtures/movies_initial_fixed.json
```

또는

```bash
python manage.py loaddata movies/fixtures/movies_initial.json
```

#### 리뷰 데이터 로드 (사용자 데이터 필요)

리뷰 fixtures를 로드하려면 먼저 사용자 데이터가 필요합니다.

**방법 1: 테스트 사용자 생성 후 로드**
```bash
# 1. 테스트 사용자 생성 (10명, 각 0개 리뷰)
python load_data.py test-data 10 0

# 2. 리뷰 fixtures 로드
python manage.py loaddata reviews/fixtures/reviews_sample.json
```

**방법 2: 자동 스크립트 사용**
```bash
python load_fixtures.py --with-reviews
```

### 4. 데이터 로드 순서

fixtures를 로드할 때는 다음 순서를 따르세요:

1. **마이그레이션** (필요시)
   ```bash
   python manage.py migrate
   ```

2. **영화 데이터** (필수)
   ```bash
   python manage.py loaddata movies/fixtures/movies_initial_fixed.json
   ```

3. **사용자 데이터** (리뷰 데이터 로드 전 필수)
   ```bash
   python load_data.py test-data 10 0
   ```

4. **리뷰 데이터** (선택사항)
   ```bash
   python manage.py loaddata reviews/fixtures/reviews_sample.json
   ```

### 5. 일반적인 오류 및 해결 방법

#### 오류: `ModuleNotFoundError: No module named 'environ'`
- **원인**: 가상환경이 활성화되지 않음
- **해결**: `source venv/Scripts/activate` (Windows) 또는 `source venv/bin/activate` (Linux/Mac) 실행

#### 오류: `User matching query does not exist` 또는 `invalid foreign key: user_id contains a value 'X' that does not have a corresponding value`
- **원인**: 리뷰 fixtures를 로드하려고 하는데 사용자 데이터가 없음
- **해결**: 먼저 사용자 데이터를 생성하세요
  ```bash
  python load_data.py test-data 10 0
  ```
  또는 자동 스크립트 사용:
  ```bash
  python load_fixtures.py --with-reviews
  ```

#### 오류: `Movie matching query does not exist`
- **원인**: 리뷰 fixtures를 로드하려고 하는데 영화 데이터가 없음
- **해결**: 먼저 영화 데이터를 로드하세요
  ```bash
  python manage.py loaddata movies/fixtures/movies_initial_fixed.json
  ```

#### 오류: 중복 키 오류 (duplicate key)
- **원인**: 이미 데이터가 존재함
- **해결**: 기존 데이터를 삭제하거나 `--skip-existing` 옵션 사용 (Django 3.2+)

### 6. 현재 데이터베이스 상태 확인

```bash
cd django-project
source venv/Scripts/activate
python manage.py shell
```

```python
from movies.models import Movie, Genre
from accounts.models import User
from reviews.models import Review

print(f"영화: {Movie.objects.count()}개")
print(f"장르: {Genre.objects.count()}개")
print(f"사용자: {User.objects.count()}개")
print(f"리뷰: {Review.objects.count()}개")
```

### 7. 전체 데이터 초기화 및 로드

데이터베이스를 완전히 초기화하려면:

```bash
# 1. 데이터베이스 삭제 (주의: 모든 데이터가 삭제됩니다)
rm db.sqlite3

# 2. 마이그레이션 파일 삭제 (선택사항, __pycache__ 제외)
# find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 3. 마이그레이션 재생성 및 적용
python manage.py makemigrations
python manage.py migrate

# 4. fixtures 로드
python load_fixtures.py --with-reviews
```

## 요약

**가장 간단한 방법:**
```bash
cd django-project
source venv/Scripts/activate  # Windows
python load_fixtures.py --with-reviews
```

이 명령으로 영화 데이터, 사용자 데이터, 리뷰 데이터가 모두 자동으로 로드됩니다.

