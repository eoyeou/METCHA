# 검색 API 옵션 비교

영화 분석 스크립트에서 사용할 수 있는 검색 API 옵션입니다.

## 1. DuckDuckGo (현재 기본 사용) ⭐ 추천

### 장점
- ✅ **완전 무료**: API 키 불필요, 제한 없음
- ✅ **빠른 응답**: 빠른 검색 속도
- ✅ **설치 간단**: `pip install duckduckgo-search`
- ✅ **프라이버시**: 검색 기록 저장 안 함

### 단점
- ⚠️ 가끔 검색 결과가 부족할 수 있음
- ⚠️ 일부 지역에서 접근 제한 가능

### 설치 및 사용
```bash
pip install duckduckgo-search
```

현재 스크립트에 이미 통합되어 있습니다.

---

## 2. Serper API

### 장점
- ✅ **빠름**: 매우 빠른 응답 속도
- ✅ **정확도 높음**: Google 검색 결과 기반
- ✅ **무료 티어**: 월 2,500회 검색

### 단점
- ⚠️ API 키 필요
- ⚠️ 무료 티어 제한

### 설치 및 사용
```bash
pip install google-search-results
```

### 코드 예시
```python
from serpapi import GoogleSearch

def search_movie_info_serper(title, release_year):
    params = {
        "q": f"{title} {release_year} movie review",
        "api_key": "YOUR_SERPER_API_KEY",
        "num": 3
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])
```

**가격**: 무료 티어 월 2,500회, 이후 $50/월 (10,000회)

---

## 3. Tavily API

### 장점
- ✅ **AI 최적화**: AI 에이전트용으로 최적화된 검색
- ✅ **구조화된 결과**: JSON 형식의 구조화된 결과
- ✅ **무료 티어**: 월 1,000회 검색

### 단점
- ⚠️ API 키 필요
- ⚠️ 무료 티어 제한이 낮음

### 설치 및 사용
```bash
pip install tavily-python
```

### 코드 예시
```python
from tavily import TavilyClient

tavily = TavilyClient(api_key="YOUR_TAVILY_API_KEY")

def search_movie_info_tavily(title, release_year):
    response = tavily.search(
        query=f"{title} {release_year} movie review plot",
        max_results=3
    )
    return response.get("results", [])
```

**가격**: 무료 티어 월 1,000회, 이후 $20/월 (10,000회)

---

## 4. Google Custom Search API

### 장점
- ✅ **높은 정확도**: Google 검색 결과
- ✅ **무료 티어**: 일 100회 검색

### 단점
- ⚠️ API 키 및 검색 엔진 ID 필요
- ⚠️ 무료 티어 제한이 매우 낮음
- ⚠️ 설정이 복잡함

### 설치 및 사용
```bash
pip install google-api-python-client
```

### 코드 예시
```python
from googleapiclient.discovery import build

service = build("customsearch", "v1", developerKey="YOUR_API_KEY")

def search_movie_info_google(title, release_year):
    result = service.cse().list(
        q=f"{title} {release_year} movie review",
        cx="YOUR_SEARCH_ENGINE_ID",
        num=3
    ).execute()
    return result.get("items", [])
```

**가격**: 무료 티어 일 100회, 이후 $5/1,000회

---

## 추천 순서

1. **DuckDuckGo** (현재 사용 중) - 무료, 제한 없음, 빠름
2. **Serper API** - 빠르고 정확하지만 무료 티어 제한
3. **Tavily API** - AI 최적화이지만 무료 티어 제한이 낮음
4. **Google Custom Search** - 정확하지만 설정 복잡, 제한 많음

## 현재 스크립트에서 다른 API 사용하기

`analyze_movie_scores.py`의 `search_movie_info` 메서드를 수정하여 다른 검색 API를 사용할 수 있습니다.

예시 (Serper API 사용):
```python
def search_movie_info(self, title: str, release_year: int) -> str:
    try:
        from serpapi import GoogleSearch
        params = {
            "q": f"{title} {release_year} movie review plot summary",
            "api_key": "YOUR_SERPER_API_KEY",
            "num": 3
        }
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results", [])
        
        if not results:
            return ""
        
        search_text = "\n\n".join([
            f"제목: {r.get('title', '')}\n내용: {r.get('snippet', '')}"
            for r in results[:3]
        ])
        return search_text
    except Exception as e:
        print(f"[경고] 검색 중 오류 발생: {e}")
        return ""
```

