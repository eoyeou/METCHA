# 🎬 AI 기반 영화 추천 및 리뷰 플랫폼

**자연어 검색과 개인화된 취향 분석을 통한 맞춤형 영화 추천 서비스**  
[노션 링크](https://www.notion.so/downtown89/2c0018db17fc801fb7f6eee10f7dba17)  
[![Django](https://img.shields.io/badge/Django-5.2.9-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=flat&logo=vue.js)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://www.python.org/)

---

## 📋 목차

- [프로젝트 소개](#프로젝트-소개)
- [팀원 정보 및 역할 분담](#팀원-정보-및-역할-분담)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [추천 알고리즘 기술적 설명](#추천-알고리즘-기술적-설명)
- [생성형 AI 활용 내용](#생성형-ai-활용-내용)
- [시작하기](#시작하기)
- [프로젝트 구조](#프로젝트-구조)
- [프로젝트 후기 및 느낀 점](#프로젝트-후기-및-느낀-점)

---

## 프로젝트 소개

기존 영화 추천 서비스는 단순 키워드 매칭 방식으로 사용자의 추상적인 요구를 충족시키기 어려웠습니다. 본 프로젝트는 **자연어 이해 기반의 의미 검색(Semantic Search)** 과 **개인화된 취향 분석**을 통해 사용자가 원하는 영화를 더 정확하게 추천하는 플랫폼을 개발했습니다.

### 핵심 가치

- 🔍 **자연어 기반 검색**: "혼자 보기 좋은 영화"와 같은 추상적 요구도 이해
- 🎯 **개인화된 추천**: 사용자의 취향을 분석하여 맞춤형 영화 추천
- 📊 **취향 분석 리포트**: 다차원적인 취향 분석을 통한 영화 선택 가이드
- 👥 **소셜 리뷰 플랫폼**: 사용자 간 리뷰 공유 및 팔로우 기능

---

## 팀원 정보 및 역할 분담

| 역할 | 이름 | 담당 영역 |
|------|------|----------|
| 팀장 | 정다운 | 백엔드 개발, AI/ML 모델 통합, 추천 알고리즘 설계 |
| 팀원 | 전연수 | 프론트엔드 개발, UI/UX 디자인, API 연동 |

### 주요 기여도

**정다운**
- Django REST Framework 기반 백엔드 API 설계 및 구현
- Sentence Transformers와 ChromaDB를 활용한 의미 기반 검색 시스템 구축
- Heaviness/Satisfaction 점수 기반 개인화 추천 알고리즘 개발
- Qwen 2.5 8B를 활용한 리뷰 데이터 보강
- 취향 분석 리포트 생성 로직 구현

**전연수**
- Vue.js 3 기반 프론트엔드 개발
- Pinia를 활용한 상태 관리 및 Vue Router를 통한 라우팅 구성
- 사용자 인터페이스 디자인 및 사용자 경험 최적화
- 백엔드 API와의 통합 및 데이터 시각화

---

## 주요 기능

### 1. 🔍 자연어 기반 영화 검색 (Semantic Search)

단순 키워드 매칭이 아닌 **의미를 이해하는 검색** 기능입니다.

**예시 검색어**
- "혼자 보기 좋은 영화"
- "비오는 날 보기 좋은 영화"
- "웃기면서도 감동적인 영화"

**동작 원리**
1. 검색어를 1024차원 임베딩 벡터로 변환 (BAAI/bge-m3)
2. ChromaDB에서 유사한 리뷰 검색 (코사인 유사도)
3. 관련 영화 추출 및 사용자 취향 반영하여 정렬

### 2. 📊 개인화된 취향 분석 리포트 (My Taste Report)

사용자가 작성한 리뷰를 기반으로 다차원적인 취향을 분석합니다.

**제공 정보**
- 📈 장르별 선호도 분포
- 🎭 선호 감독 Top 5
- ⭐ 평균 평점 및 높은 평점 영화
- 💭 한 줄 취향 요약

**특징**
- 4점 이상 평점 영화들의 Heaviness/Satisfaction 평균 계산
- 취향 변화 추적을 위한 재분석 기능 제공

### 3. 🎯 개인화된 영화 추천

**시맨틱 검색 기반 추천**
- 검색어 유사도(70%) + 사용자 취향 적합도(30%)로 점수 계산
- Heaviness/Satisfaction 점수를 활용한 개인화

**유사 영화 추천**
- 영화 상세 페이지에서 같은 장르의 영화 추천
- 평점 높은 순으로 정렬

### 4. 👥 소셜 리뷰 플랫폼

**리뷰 시스템**
- ⭐ 0.0 ~ 5.0 별점 평가
- 📝 상세 리뷰 작성 및 수정/삭제
- ⚠️ 스포일러 표시 기능
- 👍 리뷰 좋아요

**소셜 기능**
- 👤 사용자 프로필 및 팔로우/팔로워 시스템
- 📋 다른 사용자의 리뷰 탐색
- 🔗 리뷰 작성자 프로필로 바로 이동

### 5. 🎬 영화 정보 제공

- TMDB API를 통한 영화 메타데이터 수집
- 한글/영문 이중 언어 지원
- 영화 상세 정보 및 포스터 제공

---

## 기술 스택

### Backend
- **Framework**: Django 5.2.9 + Django REST Framework
- **Database**: SQLite3 (개발) / PostgreSQL (프로덕션 준비)
- **Authentication**: Token Authentication
- **API**: RESTful API

### AI/ML
- **Embedding Model**: BAAI/bge-m3 (1024차원)
- **Vector Database**: ChromaDB
- **ML Framework**: PyTorch 2.9.1
- **NLP Library**: sentence-transformers 5.2.0
- **Data Processing**: pandas, numpy

### Frontend
- **Framework**: Vue.js 3
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Build Tool**: Vite

### External API
- **TMDB API**: 영화 메타데이터 및 포스터 이미지

### Infrastructure
- **Version Control**: Git
- **Large File Storage**: Git LFS (ChromaDB 데이터)

---

## 추천 알고리즘 기술적 설명

### 1. 의미 기반 검색 (Semantic Search)

**핵심 기술**
- **임베딩 모델**: BAAI/bge-m3 (다국어 지원, 한국어 성능 우수)
- **벡터 데이터베이스**: ChromaDB (코사인 거리 기반 유사도 검색)

**알고리즘 흐름**

```
1. 검색어 입력
   ↓
2. Sentence Transformers로 임베딩 벡터 변환 (1024차원)
   ↓
3. ChromaDB에서 유사한 리뷰 검색 (코사인 유사도)
   ↓
4. 리뷰 → 영화 매핑 및 중복 제거 (최고 점수만 유지)
   ↓
5. 최종 점수 계산 및 정렬
```

**점수 계산 방식**

검색 모드에 따라 점수 계산이 달라집니다:

- **키워드 모드** (유사도 ≥ 0.9): 유사도 점수만 사용
- **의미 모드** (유사도 < 0.9): 유사도(70%) + 취향 적합도(30%)

### 2. 개인화 추천 알고리즘

**Heaviness/Satisfaction 기반 취향 적합도**

각 영화는 Heaviness(무게감)와 Satisfaction(대중성) 점수를 가지며, 사용자도 평균 취향 점수를 가집니다.

**취향 적합도 계산**

```
H_fit = 1.0 - (|User_H - Movie_H| / 100)
S_fit = 1.0 - (|User_S - Movie_S| / 100)
Preference_Fit = (H_fit + S_fit) / 2
```

**최종 점수**

```
Final_Score = Similarity × 0.7 + Preference_Fit × 0.3
```

### 3. Heaviness/Satisfaction 점수

- **Heaviness (0-100)**: 영화의 무게감, 심각성, 깊이
  - 낮음: 가벼운 코미디, 액션
  - 높음: 다큐멘터리, 사회비판 영화
  
- **Satisfaction (0-100)**: 영화의 대중성, 만족도
  - 낮음: 아트하우스, 실험적 작품
  - 높음: 블록버스터, 오락 영화

이 점수들은 GPT API를 활용하여 영화 분석 후 자동 생성됩니다.

---

## 생성형 AI 활용 내용

본 프로젝트에서는 다양한 생성형 AI 기술을 활용하여 데이터 품질 향상과 기능 구현을 진행했습니다.

### 1. 리뷰 데이터 보강 (Qwen 2.5 8B)

**목적**: 리뷰 데이터의 품질 향상 및 의미 검색 성능 개선

**활용 방식**
- Qwen 2.5 8B 모델을 사용하여 기존 리뷰 텍스트 보강
- 프롬프트 엔지니어링을 통한 구조화된 리뷰 데이터 생성
- 임베딩 생성 전 데이터 전처리 단계에서 활용

**프롬프트 전략**

리뷰 데이터를 검색 엔진에 최적화하기 위해 다음과 같은 프롬프트 전략을 사용했습니다:

**핵심 접근법**
- 리뷰어의 주관적 평가를 배제하고, 영화의 **스타일(Style)**과 **속성(Attribute)** 위주로 텍스트 재구성
- 3가지 요소(Visual, Quality, Context)로 리뷰를 분해하여 객관적인 특성 데이터 생성

**3 Factor 분석**

1. **Visual (시각/청각/스타일)**: 액션 강도, CG 스타일, 미장센, 연기톤, 화면 분위기
2. **Quality (스토리/구조/전개)**: 플롯 복잡도, 전개 속도, 장르적 특성
3. **Context (관람 상황/용도)**: 킬링타임 여부, 몰입도, 함께 보기 좋은 대상

**데이터 변환 규칙**

- 부정적 표현을 중립적 특성으로 변환
  - "지루하다" → "호흡이 긴", "서사에 집중한"
  - "뻔하다" → "장르의 문법에 충실한", "전형적인 구조의"
  - "재미없다" → "자극적이지 않고 차분한"

- 모든 서술을 긍정 평서문 또는 중립 서술문으로 작성
- 검색 엔진용 데이터로 최적화 (사람이 읽는 리뷰 요약이 아님)

**출력 형식**

```json
{
  "class": "RICH" | "IMPLICIT" | "SIMPLE" | "NOISE",
  "refined_text": "정제된 텍스트",
  "keywords": ["태그1", "태그2", "태그3"]
}
```

**효과**
- 리뷰 데이터의 품질 향상으로 의미 검색 정확도 개선
- 주관적 평가를 배제한 객관적 특성 데이터 확보
- 검색 엔진에 최적화된 구조화된 데이터 생성

### 2. 영화 점수 생성 (GPT API)

**목적**: 영화의 Heaviness/Satisfaction 점수 자동 생성

**활용 방식**
- GPT API를 활용하여 영화 메타데이터 분석
- DuckDuckGo 검색을 통한 추가 정보 수집
- 영화 특성에 맞는 점수 자동 할당 (0-100 범위)

**파일 위치**: `django-project/analyze_movie_scores.py`

**생성 데이터**
- 영화별 Heaviness 점수
- 영화별 Satisfaction 점수
- 사용자 취향 분석 및 추천 알고리즘에 활용

### 3. 텍스트 임베딩 (BAAI/bge-m3)

**목적**: 리뷰 텍스트를 벡터로 변환하여 의미 검색 구현

**활용 방식**
- BAAI/bge-m3 모델을 사용하여 리뷰 텍스트를 1024차원 벡터로 변환
- ChromaDB에 임베딩 벡터 저장
- 검색어와 리뷰 간 유사도 계산

**파일 위치**
- `django-project/reviews/embedding_utils.py`: 임베딩 생성 유틸리티
- `django-project/reviews/chroma_utils.py`: ChromaDB 검색 유틸리티

**효과**
- 키워드 매칭을 넘어선 의미 기반 검색 구현
- 자연어 쿼리 이해 및 관련 영화 추천

### 4. 데이터 번역 (선택적)

**목적**: 다국어 리뷰 데이터 지원

**활용 방식**
- 리뷰 데이터 번역을 위한 AI 모델 활용
- 영어/한국어 이중 언어 지원

---

## 시작하기

### 필수 요구사항

- Python 3.11+
- Node.js 18+
- Git
- Git LFS (ChromaDB 데이터 다운로드용)

### 설치 및 실행

#### 1. 저장소 클론

```bash
git clone <repository-url>
cd final-pjt
```

#### 2. 백엔드 설정

```bash
cd django-project

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
# SECRET_KEY, DEBUG, TMDB_API_KEY 설정 필요

# 데이터베이스 마이그레이션
python manage.py migrate

# Fixture 데이터 로드
python manage.py loaddata movies/fixtures/movies_initial_fixed.json
python manage.py loaddata db_backup.json
```

#### 3. ChromaDB 데이터 설정

ChromaDB 데이터는 별도 저장소에서 관리됩니다:

```bash
# ChromaDB 저장소 클론
git clone https://lab.ssafy.com/rhseb963/final-chroma-db.git chromadb-temp
cd chromadb-temp

# Git LFS 파일 다운로드
git lfs install
git lfs pull

# django-project로 복사
cp -r chroma_db ../django-project/
cd ..
rm -rf chromadb-temp
```

#### 4. 프론트엔드 설정

```bash
cd vue-project
npm install
npm run dev
```

#### 5. 서버 실행

```bash
# 백엔드 (터미널 1)
cd django-project
source venv/bin/activate
python manage.py runserver

# 프론트엔드 (터미널 2)
cd vue-project
npm run dev
```

### 접속 정보

- **프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/

---

## 프로젝트 구조

```
final-pjt/
├── django-project/          # Django 백엔드
│   ├── accounts/            # 사용자 관리 앱
│   ├── movies/              # 영화 관리 앱
│   │   └── search_views.py  # 의미 기반 검색 API
│   ├── reviews/             # 리뷰 관리 앱
│   │   ├── embedding_utils.py  # 임베딩 생성
│   │   └── chroma_utils.py     # ChromaDB 검색
│   ├── watchlists/          # 보고싶은 영화 목록 앱
│   ├── chroma_db/           # ChromaDB 데이터 (Git LFS)
│   ├── db.sqlite3           # SQLite 데이터베이스
│   └── requirements.txt     # Python 의존성
│
├── vue-project/             # Vue.js 프론트엔드
│   ├── src/
│   │   ├── views/           # 페이지 컴포넌트
│   │   ├── components/      # 재사용 컴포넌트
│   │   ├── stores/          # Pinia 상태 관리
│   │   └── router/          # Vue Router 설정
│   └── package.json         # Node.js 의존성
│
├── ARCHITECTURE.md          # 시스템 아키텍처 문서
├── PROJECT_SETUP_GUIDE.md   # 프로젝트 세팅 가이드
└── README.md                # 프로젝트 README
```

---

## 프로젝트 후기 및 느낀 점

### 기술적 성취

본 프로젝트를 통해 **의미 기반 검색(Semantic Search)** 과 **벡터 데이터베이스**라는 최신 기술을 실제로 구현해볼 수 있었습니다. 단순 키워드 매칭을 넘어서 사용자의 의도를 이해하는 검색 시스템을 구축하는 과정에서 자연어 처리와 임베딩 기술의 중요성을 깊이 이해할 수 있었습니다.

특히 ChromaDB를 활용한 벡터 검색 구현을 통해 대용량 임베딩 데이터를 효율적으로 관리하고 검색하는 방법을 학습했습니다. 또한 사용자 취향 점수(Heaviness/Satisfaction)를 도입하여 개인화 추천의 정확도를 높일 수 있었던 점이 가장 큰 성취였습니다.

### AI 활용의 한계와 극복

생성형 AI를 활용한 데이터 보강 과정에서 **프롬프트 엔지니어링** 의 중요성을 체감했습니다. Qwen 2.5 8B를 사용한 리뷰 데이터 보강 시, 초기에는 원하는 품질의 결과를 얻기 어려웠지만, 프롬프트를 반복적으로 개선하면서 점차 만족스러운 결과를 얻을 수 있었습니다.

또한 GPT API를 활용한 영화 점수 생성 과정에서 API 호출 비용과 처리 시간을 고려한 최적화가 필요하다는 것을 배웠습니다. 배치 처리와 캐싱 전략을 통해 효율적인 데이터 생성 파이프라인을 구축할 수 있었습니다.

### 성능 최적화의 필요성

의미 기반 검색 시스템을 구현하면서 **성능 최적화**의 필요성을 절감했습니다. 초기에는 모든 리뷰를 순차적으로 처리하여 검색 속도가 느렸지만, ChromaDB의 인덱싱 기능과 벡터 검색 최적화를 통해 검색 속도를 크게 개선할 수 있었습니다.

또한 같은 영화의 여러 리뷰가 검색 결과에 중복으로 나타나는 문제를 해결하기 위해 최고 점수만 유지하는 중복 제거 로직을 구현하는 과정에서 알고리즘 설계의 중요성을 배웠습니다.

### 향후 개선 방향

현재 시스템은 기본적인 의미 검색과 개인화 추천을 제공하지만, 다음과 같은 개선이 필요하다고 생각합니다:

1. **실시간 학습**: 사용자의 피드백을 반영하여 추천 모델을 지속적으로 개선
2. **캐싱 전략**: Redis 등을 활용한 검색 결과 캐싱으로 응답 속도 개선
3. **다양한 추천 알고리즘**: 협업 필터링, 콘텐츠 기반 필터링 등 다양한 추천 방식 도입
4. **시각화 개선**: 취향 분석 리포트의 시각화를 더욱 직관적으로 개선
5. **확장성**: 대용량 데이터 처리를 위한 마이크로서비스 아키텍처 고려

### 결론

본 프로젝트를 통해 최신 AI/ML 기술을 실제 서비스에 적용해보는 소중한 경험을 할 수 있었습니다. 특히 의미 기반 검색이라는 차별화된 기능을 구현하면서, 단순 기술 구현을 넘어서 사용자 경험을 고려한 서비스 설계의 중요성을 배울 수 있었습니다. 앞으로도 지속적인 학습과 개선을 통해 더 나은 서비스를 만들어나가고 싶습니다.

---