# 영화 Heaviness & Satisfaction 분석 가이드

## 개요

이 스크립트는 영화의 **Heaviness(무게감)**와 **Satisfaction(대중성)** 점수를 GPT 5 mini API를 사용하여 자동으로 분석하고 DB에 저장합니다.

## 설치

### 1. 필요한 패키지 설치

```bash
cd django-project
source venv/Scripts/activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

pip install duckduckgo-search tqdm
```

### 2. 마이그레이션 확인

마이그레이션이 이미 적용되어 있어야 합니다:

```bash
python manage.py migrate movies
```

## 사용법

### 기본 사용 (전체 영화 분석)

```bash
python analyze_movie_scores.py
```

### 제한된 수만큼 분석 (테스트용)

```bash
python analyze_movie_scores.py --limit 10
```

### 특정 영화만 분석

```bash
python analyze_movie_scores.py --movie-id 1
```

### 검색 기능 없이 분석 (더 빠름, 하지만 정확도 낮을 수 있음)

```bash
python analyze_movie_scores.py --no-search
```

## 점수 기준

### Heaviness (무게감, 0-100)
- **0-30**: 가볍고 오락적인 영화
  - 예: 코미디, 액션, 로맨스, 뮤지컬
- **31-60**: 중간 수준의 무게감
  - 예: 드라마, 스릴러, 미스터리
- **61-100**: 무겁고 진지한 영화
  - 예: 사회비판, 철학적 주제, 다큐멘터리, 전쟁 영화

### Satisfaction (대중성, 0-100)
- **0-30**: 소수 취향, 비주류 영화
  - 예: 아트하우스, 실험적 영화
- **31-60**: 일반적인 대중 영화
  - 예: 일반적인 상업 영화
- **61-100**: 대중적으로 인기 있는 영화
  - 예: 블록버스터, 히트작, 시리즈 영화

## 검색 API 옵션

현재 스크립트는 **DuckDuckGo**를 기본 검색 엔진으로 사용합니다.

### DuckDuckGo (현재 사용 중)
- ✅ **무료**: 완전 무료
- ✅ **제한 없음**: API 키 불필요
- ✅ **빠름**: 빠른 응답 속도
- ✅ **설치**: `pip install duckduckgo-search`

### 다른 검색 API 옵션

필요한 경우 다음 API로 변경 가능합니다:

1. **Serper API** (https://serper.dev)
   - 무료 티어: 월 2,500회 검색
   - 빠른 응답 속도
   - API 키 필요

2. **Tavily API** (https://tavily.com)
   - 무료 티어: 월 1,000회 검색
   - AI 최적화 검색
   - API 키 필요

3. **Google Custom Search API**
   - 무료 티어: 일 100회 검색
   - 높은 정확도
   - API 키 필요

## 동작 방식

1. **기본 정보 수집**: 영화 제목, 설명, 감독, 출연진 등
2. **검색 정보 수집** (옵션): DuckDuckGo로 추가 정보 검색
3. **GPT 5 mini API 호출**: 수집한 정보를 바탕으로 점수 분석
4. **결과 저장**: DB에 `heaviness`와 `satisfaction` 필드 업데이트

## 주의사항

1. **API 호출 제한**: GPT 5 mini API의 호출 제한을 확인하세요
2. **처리 시간**: 영화당 약 2-5초 소요 (검색 포함 시)
3. **비용**: GPT 5 mini API 사용 비용이 발생할 수 있습니다
4. **검색 실패**: 검색이 실패해도 기본 정보만으로 분석을 시도합니다

## 문제 해결

### 검색 엔진 초기화 실패
```bash
pip install --upgrade duckduckgo-search
```

### JSON 파싱 오류
- GPT 응답이 JSON 형식이 아닐 수 있습니다
- 스크립트가 자동으로 재시도하거나 다음 영화로 넘어갑니다

### API 호출 실패
- 네트워크 연결 확인
- GMS_KEY 확인
- API 엔드포인트 확인

## 추후 활용

이 두 지표(Heaviness, Satisfaction)를 사용하여 사용자 취향을 4가지 유형으로 분류할 수 있습니다:

1. **High Heaviness + High Satisfaction**: 진지한 대중 영화
2. **High Heaviness + Low Satisfaction**: 진지한 비주류 영화
3. **Low Heaviness + High Satisfaction**: 가벼운 대중 영화
4. **Low Heaviness + Low Satisfaction**: 가벼운 비주류 영화

