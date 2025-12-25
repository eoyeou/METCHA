# 프로젝트 세팅 가이드 (새 컴퓨터)

이 문서는 완전히 새로운 컴퓨터에 프로젝트를 설정하는 전체 절차를 설명합니다.

## 목차

1. [필수 요구사항](#1-필수-요구사항)
2. [프로젝트 다운로드](#2-프로젝트-다운로드)
3. [백엔드 설정 (Django)](#3-백엔드-설정-django)
4. [ChromaDB 데이터 복사](#4-chromadb-데이터-복사)
5. [프론트엔드 설정 (Vue.js)](#5-프론트엔드-설정-vuejs)
6. [서버 실행 및 테스트](#6-서버-실행-및-테스트)
7. [문제 해결](#7-문제-해결)

---

## 1. 필수 요구사항

### 필수 설치 항목

- **Python 3.11+** (권장: 3.11)
- **Node.js 18+** 및 npm
- **Git**

### 확인 방법

```bash
python3 --version  # Python 3.11.x 이상
node --version     # Node.js 18.x 이상
npm --version      # npm 9.x 이상
git --version      # Git 설치 확인
```

---

## 2. 프로젝트 다운로드

### 방법 1: Git 클론 (권장)

```bash
# 저장소 클론
git clone <repository-url>
cd final-pjt
```

### 방법 2: ZIP 파일 다운로드

```bash
# ZIP 파일을 다운로드하고 압축 해제
unzip final-pjt.zip
cd final-pjt
```

---

## 3. 백엔드 설정 (Django)

### 3.1. 가상환경 생성 및 활성화

```bash
cd django-project

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

### 3.2. 의존성 설치

```bash
# 가상환경이 활성화된 상태에서
pip install --upgrade pip
pip install -r requirements.txt
```

**주의**: 
- `torch` (PyTorch)와 `sentence-transformers`가 포함되어 있어 설치 시간이 오래 걸릴 수 있습니다.
- GPU가 있는 경우 PyTorch가 자동으로 GPU 버전을 설치합니다.

### 3.3. 환경 변수 설정

`django-project` 디렉토리에 `.env` 파일을 생성합니다:

```bash
cd django-project
touch .env  # 또는 Windows: type nul > .env
```

`.env` 파일 내용:

```env
# Django 설정
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=True

# TMDB API 키 (필수)
TMDB_API_KEY=your-tmdb-api-key-here
```

**SECRET_KEY 생성 방법**:

```bash
# Python으로 생성
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 또는 Django shell 사용
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

**TMDB API 키 발급**:
1. https://www.themoviedb.org/ 접속
2. 회원가입 후 API 키 발급
3. `.env` 파일에 `TMDB_API_KEY` 값 설정

### 3.4. Django 데이터베이스 설정

#### 방법 A: SQLite DB 파일 복사 (권장, 빠름)

기존 컴퓨터에서 다음 파일을 복사합니다:

```
django-project/db.sqlite3
```

새 컴퓨터의 `django-project/` 디렉토리에 복사합니다.

```bash
# 복사 후 마이그레이션 상태 확인
python manage.py migrate
```

#### 방법 B: Fixture 파일로 데이터 로드

```bash
# 마이그레이션 실행
python manage.py migrate

# Fixture 파일로 데이터 로드
python manage.py loaddata movies/fixtures/movies_initial_fixed.json
python manage.py loaddata db_backup.json
```

**주의**: 
- `db_backup.json`에는 사용자, 리뷰, 팔로우 관계 등이 포함됩니다.
- `movies_initial_fixed.json`에는 영화 데이터와 Heaviness/Satisfaction 점수가 포함됩니다.

### 3.5. 관리자 계정 생성 (선택사항)

```bash
python manage.py createsuperuser
```

---

## 4. ChromaDB 데이터 복사

### ⚠️ 중요: ChromaDB 데이터는 반드시 복사해야 합니다!

ChromaDB는 의미 기반 검색 기능에 필수적입니다. 임베딩 데이터를 다시 생성하는 것은 매우 오래 걸리므로, 기존 데이터를 복사하는 것이 좋습니다.

### 4.1. ChromaDB 디렉토리 복사

기존 컴퓨터에서 다음 디렉토리 전체를 복사합니다:

```
django-project/chroma_db/
```

새 컴퓨터의 `django-project/` 디렉토리에 복사합니다.

**디렉토리 구조**:
```
chroma_db/
├── chroma.sqlite3          # 메타데이터
├── 40bda34d-.../          # 컬렉션 데이터
│   ├── data_level0.bin
│   ├── header.bin
│   ├── length.bin
│   └── link_lists.bin
└── d1f74a5e-.../          # 컬렉션 데이터
    ├── data_level0.bin
    ├── header.bin
    ├── length.bin
    └── link_lists.bin
```

### 4.2. 복사 방법

#### 방법 1: 직접 복사 (로컬)

```bash
# 기존 컴퓨터에서
cd django-project
tar -czf chroma_db.tar.gz chroma_db/

# 새 컴퓨터에서
cd django-project
tar -xzf chroma_db.tar.gz
```

#### 방법 2: Git LFS (대용량 파일)

ChromaDB 파일이 크면 Git LFS를 사용할 수 있습니다 (이미 설정되어 있는 경우).

```bash
git lfs install
git lfs pull
```

#### 방법 3: rsync/SCP (원격)

```bash
# 원격 서버에서 복사
rsync -avz user@remote:/path/to/final-pjt/django-project/chroma_db/ ./chroma_db/
# 또는
scp -r user@remote:/path/to/final-pjt/django-project/chroma_db/ ./chroma_db/
```

### 4.3. 별도 Git 저장소에서 ChromaDB 가져오기 (권장)

ChromaDB 데이터를 별도 Git 저장소에 올려두었다면, 다음과 같이 가져올 수 있습니다:

```bash
# 1. 별도 저장소 클론 (예: chromadb-data 저장소)
git clone <chromadb-repository-url> chromadb-temp
cd chromadb-temp

# 2. chroma_db 디렉토리를 django-project로 복사
cp -r chroma_db ../django-project/  # macOS/Linux
# 또는 Windows: xcopy /E /I chroma_db ..\django-project\chroma_db

# 3. 임시 디렉토리 삭제 (선택사항)
cd ..
rm -rf chromadb-temp
```

**또는 직접 pull 받기**:

```bash
# django-project 디렉토리에서
cd django-project

# 별도 저장소를 서브모듈이나 직접 클론
git clone <chromadb-repository-url> chromadb-temp
cp -r chromadb-temp/chroma_db ./
rm -rf chromadb-temp
```

**주의사항**:
- ChromaDB 디렉토리가 크면 Git LFS를 사용하는 것이 좋습니다.
- 일반 Git은 대용량 파일에 최적화되어 있지 않아 느릴 수 있습니다.

### 4.4. ChromaDB 재생성 (복사가 불가능한 경우)

ChromaDB 데이터를 복사할 수 없는 경우, Parquet 파일에서 재생성할 수 있습니다:

**필요한 파일**:
- `django-project/review_embeddings_final.parquet`

```bash
cd django-project
source venv/bin/activate  # 가상환경 활성화

# ChromaDB 생성
python create_chroma_db.py
```

**주의**:
- Parquet 파일이 없으면 ChromaDB를 재생성할 수 없습니다.
- 재생성은 시간이 오래 걸릴 수 있습니다 (수백~수천 개의 리뷰 임베딩 처리).

### 4.5. ChromaDB 확인

ChromaDB가 제대로 복사되었는지 확인:

```bash
cd django-project
source venv/bin/activate
python manage.py shell
```

```python
from reviews.chroma_utils import get_collection_stats

stats = get_collection_stats()
print(f"총 리뷰 수: {stats['total_reviews']}")
print(f"DB 경로: {stats['db_path']}")

# 테스트 검색
from reviews.embedding_utils import embed_text
from reviews.chroma_utils import search_similar_reviews

query_embedding = embed_text("테스트")
results = search_similar_reviews(query_embedding, n_results=5)
print(f"검색 결과: {len(results)}개")
```

---

## 5. 프론트엔드 설정 (Vue.js)

### 5.1. 의존성 설치

```bash
cd vue-project
npm install
```

### 5.2. 환경 변수 설정 (필요한 경우)

프로젝트에 `.env` 파일이 필요하면 생성합니다 (현재는 설정 파일에 하드코딩된 경우가 많음).

### 5.3. 개발 서버 실행

```bash
npm run dev
```

프론트엔드는 기본적으로 `http://localhost:5173`에서 실행됩니다.

---

## 6. 서버 실행 및 테스트

### 6.1. Django 백엔드 서버 실행

```bash
cd django-project
source venv/bin/activate  # 가상환경 활성화

# 개발 서버 실행
python manage.py runserver
```

백엔드는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### 6.2. 전체 시스템 테스트

#### 1) 백엔드 API 테스트

```bash
# Django 서버가 실행 중인 상태에서
curl http://localhost:8000/api/movies/
```

#### 2) 의미 기반 검색 테스트

```bash
curl -X POST http://localhost:8000/api/movies/search/semantic/ \
  -H "Content-Type: application/json" \
  -d '{"query": "혼자 보기 좋은 영화", "limit": 10}'
```

#### 3) 프론트엔드 접속

브라우저에서 `http://localhost:5173` 접속하여 웹사이트가 정상 작동하는지 확인합니다.

### 6.3. 데이터베이스 확인

```bash
cd django-project
source venv/bin/activate
python manage.py shell
```

```python
from movies.models import Movie
from accounts.models import User
from reviews.models import Review
from reviews.chroma_utils import get_collection_stats

# 영화 데이터 확인
print(f"영화 수: {Movie.objects.count()}")
print(f"사용자 수: {User.objects.count()}")
print(f"리뷰 수: {Review.objects.count()}")

# ChromaDB 확인
stats = get_collection_stats()
print(f"ChromaDB 리뷰 수: {stats['total_reviews']}")
```

---

## 7. 문제 해결

### 문제 1: ChromaDB 컬렉션을 찾을 수 없습니다

**오류 메시지**:
```
컬렉션 'review_embeddings'을 찾을 수 없습니다.
```

**해결 방법**:
1. `chroma_db/` 디렉토리가 올바른 위치에 있는지 확인 (`django-project/chroma_db/`)
2. 디렉토리 권한 확인
3. ChromaDB 재생성 (Parquet 파일 필요)

### 문제 2: 임베딩 모델 로딩 실패

**오류 메시지**:
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**해결 방법**:
```bash
cd django-project
source venv/bin/activate
pip install sentence-transformers
```

### 문제 3: TMDB API 오류

**오류 메시지**:
```
TMDB API Key가 유효하지 않습니다
```

**해결 방법**:
1. `.env` 파일에 `TMDB_API_KEY`가 올바르게 설정되었는지 확인
2. TMDB API 키가 유효한지 확인 (https://www.themoviedb.org/)

### 문제 4: 마이그레이션 오류

**해결 방법**:
```bash
# 마이그레이션 파일 삭제 후 재생성 (주의: 기존 DB가 있으면 백업)
python manage.py migrate --run-syncdb
```

### 문제 5: 포트 충돌

**해결 방법**:
- Django: `python manage.py runserver 8001` (다른 포트 사용)
- Vue: `npm run dev -- --port 5174` (다른 포트 사용)

---

## 요약 체크리스트

새 컴퓨터에서 프로젝트를 설정할 때 다음 항목을 확인하세요:

### 백엔드
- [ ] Python 3.11+ 설치
- [ ] 가상환경 생성 및 활성화
- [ ] `requirements.txt` 의존성 설치
- [ ] `.env` 파일 생성 (SECRET_KEY, DEBUG, TMDB_API_KEY)
- [ ] Django 마이그레이션 실행
- [ ] Django DB 데이터 복사/로드 (`db.sqlite3` 또는 fixture)
- [ ] **ChromaDB 디렉토리 복사** (`chroma_db/`) ⚠️ 중요!
- [ ] Django 서버 실행 확인

### 프론트엔드
- [ ] Node.js 18+ 설치
- [ ] `npm install` 실행
- [ ] Vue 개발 서버 실행 확인

### 테스트
- [ ] 백엔드 API 접속 확인
- [ ] 의미 기반 검색 작동 확인
- [ ] 프론트엔드 웹사이트 접속 확인

---

## 추가 정보

### 파일 크기 예상

- `chroma_db/` 디렉토리: 수백 MB ~ 수 GB (리뷰 수에 따라 다름)
- `db.sqlite3`: 수십 MB
- `review_embeddings_final.parquet`: 수백 MB (선택사항, ChromaDB 재생성 시 필요)

### 네트워크 전송 시 주의사항

ChromaDB 디렉토리를 전송할 때:
- **별도 Git 저장소 사용** (권장): Git LFS 설정 권장, 버전 관리 용이
- 압축 파일로 전송: tar.gz, zip 사용
- Git LFS 사용 시 설정 확인 필수 (대용량 파일)
- rsync/SCP 사용 시 `-avz` 옵션 권장

### 별도 Git 저장소 설정 예시 (참고)

별도 저장소에 ChromaDB를 올릴 때:

```bash
# 1. 새 저장소 생성 (예: chromadb-data)
mkdir chromadb-data
cd chromadb-data
git init

# 2. Git LFS 설정 (대용량 파일용, 권장)
git lfs install
git lfs track "*.bin"
git lfs track "*.sqlite3"

# 3. ChromaDB 디렉토리 복사
cp -r /path/to/django-project/chroma_db ./

# 4. 커밋 및 푸시
git add .gitattributes chroma_db/
git commit -m "Add ChromaDB data"
git remote add origin <repository-url>
git push -u origin main
```

**새 컴퓨터에서 받기** (이미 위 4.3 섹션에 설명됨):
```bash
git clone <repository-url> chromadb-temp
cp -r chromadb-temp/chroma_db ./django-project/
rm -rf chromadb-temp
```

---

## 문의

문제가 발생하면 프로젝트 관리자에게 문의하세요.
