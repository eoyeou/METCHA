# TMDB API 이용 허락 조건

## 개요

본 프로젝트는 **The Movie Database (TMDB) API**를 사용하여 영화 데이터를 수집합니다.

## TMDB API 이용 허락 조건

### 1. 기본 이용 조건

TMDB API는 **무료**로 제공되며, 다음 조건을 준수해야 합니다:

- ✅ **비상업적 용도**: 개인 프로젝트, 교육 목적, 포트폴리오 등
- ✅ **상업적 용도**: TMDB에 별도 문의 필요 (https://www.themoviedb.org/contact)

### 2. 필수 요구사항

1. **TMDB 로고/크레딧 표시**
   - TMDB 데이터를 사용하는 경우, TMDB 로고와 "This product uses the TMDB API but is not endorsed or certified by TMDB" 문구를 표시해야 합니다.

2. **API 키 관리**
   - API 키는 안전하게 관리해야 하며, 공개 저장소에 노출되지 않도록 해야 합니다.
   - 현재 프로젝트에서는 `.env` 파일을 통해 관리합니다.

3. **Rate Limiting**
   - TMDB API는 초당 40개 요청으로 제한됩니다.
   - 현재 스크립트는 이 제한을 준수하도록 설계되었습니다.

### 4. 데이터 사용 규칙

- ✅ **영화 메타데이터**: 제목, 설명, 포스터, 감독, 출연진 등
- ✅ **장르 정보**: 영화 장르 분류
- ❌ **이미지 직접 저장**: 포스터 이미지는 TMDB URL을 참조만 하고, 직접 다운로드하여 저장하지 않습니다.

### 5. 라이선스 정보

- **TMDB 데이터**: Creative Commons Attribution-ShareAlike 4.0 International License
- **TMDB 로고**: TMDB 소유, 사용 시 라이선스 확인 필요

## 현재 프로젝트에서의 사용

### 사용 목적
- 영화 정보 데이터베이스 구축
- 영화 추천 시스템 개발
- 사용자 취향 분석

### 사용 데이터
- 영화 제목 (한국어, 영어)
- 영화 설명 (한국어, 영어)
- 포스터 URL
- 감독 정보
- 출연진 정보
- 장르 정보
- 개봉 연도
- 상영 시간

### 데이터 수집 방법
- `load_data.py`: TMDB API를 통해 영화 데이터 수집
- 주기적 업데이트 기능 포함 (`update-empty`, `update-all`)

## 참고 자료

- **TMDB 공식 사이트**: https://www.themoviedb.org/
- **TMDB API 문서**: https://developers.themoviedb.org/3
- **이용 약관**: https://www.themoviedb.org/terms-of-use
- **API 키 발급**: https://www.themoviedb.org/settings/api

## 준수 사항 확인

- ✅ API 키를 환경 변수로 관리 (공개 저장소에 노출되지 않음)
- ✅ Rate Limiting 준수 (초당 40개 요청 이하)
- ✅ 이미지 직접 저장하지 않음 (URL 참조만)
- ✅ 비상업적/교육 목적 사용
- ⚠️ TMDB 크레딧 표시 필요 (프론트엔드에 추가 권장)

## 권장 사항

프론트엔드에 다음 크레딧을 추가하는 것을 권장합니다:

```
This product uses the TMDB API but is not endorsed or certified by TMDB.
```

또는 TMDB 로고를 표시할 수 있습니다.

