# Archive 폴더

이 폴더는 프로젝트 개발 과정에서 사용되었지만 현재는 더 이상 필요하지 않은 파일들을 보관하는 곳입니다.

## 폴더 구조

### `scripts/`
임시 테스트 스크립트 및 개발 중 사용한 유틸리티 스크립트들
- `check_*.py`: 데이터 검증용 임시 스크립트
- `test_*.py`: 기능 테스트용 임시 스크립트
- `estimate_translation_time.py`: 번역 시간 추정 스크립트
- `kaggle_*.py`: Kaggle에서 사용한 번역 스크립트
- `import_translated_reviews.py`: 번역 리뷰 임포트 스크립트
- `merge_translated_reviews.py`: 번역 파일 병합 스크립트
- `translate_reviews.py`: 리뷰 번역 스크립트
- `fix_movie_genres.py`: 장르 수정 스크립트
- `load_more_reviews.py`: 추가 리뷰 로드 스크립트
- `create_*.py`: Fixture 생성 스크립트

### `data/`
처리 완료된 중간 데이터 파일들
- `reviews_input*.json`: 번역을 위한 입력 데이터
- `reviews_preprocessing.json`: 전처리된 리뷰 데이터
- `reviews_translated*.json`: 번역 완료된 리뷰 데이터

**참고**: 이미 DB에 반영되었거나 더 이상 필요하지 않은 데이터 파일들입니다.

### `docs/`
중복되거나 구버전 문서들
- `KAGGLE_TRANSLATION_GUIDE.md`: Kaggle 번역 가이드
- `translation_guide.md`: 번역 가이드
- `mbart_guide.md`: MBart 번역 모델 가이드
- `papago_api_info.md`: Papago API 정보
- `MOVIE_ANALYSIS_GUIDE.md`: 영화 분석 가이드
- `FIXTURES_LOAD_GUIDE.md`: Fixture 로드 가이드
- `SEARCH_ISSUE_FIX.md`: 검색 이슈 해결 가이드 (해결 완료)
- `SEARCH_API_OPTIONS.md`: 검색 API 옵션 문서
- `EMBEDDING_MODEL_OPTIONS.md`: 임베딩 모델 옵션 문서
- `CHROMADB_GUIDE.md`: ChromaDB 가이드 (이미 PROJECT_SETUP_GUIDE.md에 통합)
- `NF03_REQUIREMENTS.md`: 프로젝트 요구사항 문서

**참고**: 핵심 문서는 프로젝트 루트의 `README.md`, `ARCHITECTURE.md`, `PROJECT_SETUP_GUIDE.md`에 통합되어 있습니다.

### `backups/`
데이터베이스 백업 파일들
- `db.sqlite3.backup.*`: SQLite 데이터베이스 백업 파일

**참고**: 최신 데이터는 `db_backup.json` fixture 파일이나 Git 저장소에 있습니다.

### `chromadb-repo/`
ChromaDB 데이터를 별도 Git 저장소로 분리하기 전의 로컬 저장소

**참고**: 현재는 별도 저장소 (https://lab.ssafy.com/rhseb963/final-chroma-db.git)에서 관리됩니다.

---

## 삭제 시 주의사항

이 폴더의 파일들은 프로젝트 개발 과정의 기록으로 보관하고 있습니다. 삭제하기 전에 다음을 확인하세요:

1. **데이터 파일**: 이미 DB에 반영되었는지 확인
2. **스크립트 파일**: 필요시 참고용으로 사용 가능
3. **문서 파일**: 핵심 정보가 다른 문서에 통합되었는지 확인
4. **백업 파일**: 최신 백업이 다른 곳에 있는지 확인

필요시 이 폴더 전체를 삭제해도 프로젝트 실행에는 영향이 없습니다.
