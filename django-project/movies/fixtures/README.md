# 영화 데이터 Fixture

## 개요

이 디렉토리에는 Django fixture 형식으로 저장된 영화 데이터가 포함되어 있습니다.

## 파일 설명

- `movies_initial.json`: 초기 영화 데이터 (200개 영화 + 장르 정보)

## 데이터 로드 방법

### 1. Fixture로 데이터 로드

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

python manage.py loaddata movies/fixtures/movies_initial.json
```

### 2. TMDB API로 직접 데이터 로드

```bash
cd django-project
source venv/Scripts/activate

# 전체 데이터 로드 (장르 + 영화)
python load_data.py

# 장르만 로드
python load_data.py genres

# 영화만 로드 (기본 10페이지)
python load_data.py movies 10
```

## 데이터 업데이트

### 설명이 비어있는 영화만 업데이트
```bash
python load_data.py update-empty
```

### 모든 영화 설명 업데이트
```bash
python load_data.py update-all
```

## 데이터 통계

- **총 영화 수**: 200개 (요구사항: 최소 50개 ✅)
- **장르 수**: 약 20개
- **데이터 소스**: TMDB (The Movie Database) API

## 주의사항

1. Fixture를 로드하기 전에 마이그레이션을 먼저 실행해야 합니다:
   ```bash
   python manage.py migrate
   ```

2. 기존 데이터가 있는 경우 덮어쓰기 될 수 있으므로 주의하세요.

3. TMDB API 키가 필요합니다 (`pjt/settings.py`에 설정).

