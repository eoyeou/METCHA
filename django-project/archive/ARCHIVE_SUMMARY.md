# Archive 폴더 정리 요약

**정리 날짜**: 2025-12-26

## 정리된 파일 목록

### scripts/ (임시 스크립트)
- `check_env.py`
- `check_failed_movies.py`
- `check_movie_scores.py`
- `check_review_length.py`
- `create_fixture.py`
- `create_reviews_fixture.py`
- `create_users_for_reviews.py`
- `estimate_translation_time.py`
- `fix_movie_genres.py`
- `import_translated_reviews.py`
- `kaggle_notebook_example.py`
- `kaggle_translate_reviews.py`
- `load_more_reviews.py`
- `merge_translated_reviews.py`
- `test_chroma_search.py`
- `test_login.py`
- `test_tmdb_api.py`
- `translate_reviews.py`
- `migrations/add_original_content.py` (임시 마이그레이션 스크립트)

### data/ (처리 완료된 데이터 파일)
- `reviews_input.json`
- `reviews_input_part01.json`
- `reviews_input_part02.json`
- `reviews_preprocessing.json`
- `reviews_translated_en_to_ko.json`

### docs/ (중복/구버전 문서)
- `CHROMADB_GUIDE.md`
- `EMBEDDING_MODEL_OPTIONS.md`
- `FIXTURES_LOAD_GUIDE.md`
- `KAGGLE_TRANSLATION_GUIDE.md`
- `MOVIE_ANALYSIS_GUIDE.md`
- `NF03_REQUIREMENTS.md`
- `SEARCH_API_OPTIONS.md`
- `SEARCH_ISSUE_FIX.md`
- `mbart_guide.md`
- `papago_api_info.md`
- `translation_guide.md`

### backups/ (백업 파일)
- `db.sqlite3.backup.20251226_005035`

### chromadb-repo/ (별도 저장소로 분리 전 로컬 저장소)
- ChromaDB 데이터 (이미 별도 Git 저장소로 분리됨)

## 남은 필수 파일들

### Python 스크립트
- `manage.py` - Django 관리 스크립트
- `analyze_movie_scores.py` - 영화 점수 분석 (GPT API 사용)
- `create_chroma_db.py` - ChromaDB 생성 스크립트
- `load_data.py` - 데이터 로드 스크립트
- `load_fixtures.py` - Fixture 로드 스크립트

### 문서
- `AI_SEMANTIC_SEARCH_EXPLANATION.md` - AI 의미 검색 설명
- `SEARCH_DUPLICATE_REMOVAL_ANALYSIS.md` - 검색 중복 제거 분석
- `SEARCH_IMPLEMENTATION.md` - 검색 구현 가이드
- `TMDB_API_LICENSE.md` - TMDB API 라이선스

### 데이터베이스
- `db.sqlite3` - SQLite 데이터베이스
- `db_backup.json` - 데이터베이스 백업 (Fixture)

### 데이터 파일
- `review_embeddings_final.parquet` - 리뷰 임베딩 데이터 (ChromaDB 재생성 시 필요)

## 핵심 문서 위치

프로젝트 루트 (`final-pjt/`)의 주요 문서:
- `README.md` - 프로젝트 전체 README
- `ARCHITECTURE.md` - 시스템 아키텍처 문서
- `PROJECT_SETUP_GUIDE.md` - 프로젝트 세팅 가이드
- `PPT_CONTENT.md` - PPT 슬라이드 내용
- `PPT_TECH_DIFFERENTIATION.md` - 기술 차별성 문서
- `HEAVINESS_SATISFACTION_EXPLANATION.md` - Heaviness/Satisfaction 지표 설명
- `SIMILAR_MOVIES_SCENARIO.md` - 유사 영화 추천 시나리오

## 참고사항

이 archive 폴더의 파일들은 개발 과정의 기록으로 보관하고 있습니다. 프로젝트 실행에는 필수적이지 않으므로 필요시 삭제 가능합니다.
