# 리뷰 번역 가이드

## 번역 방법 비교

### 1. googletrans (추천 - 무료)
- **장점**: 무료, 설치 간단, 사용 쉬움
- **단점**: 제한적 (하루 약 15,000자), 가끔 불안정
- **설치**: `pip install googletrans==4.0.0rc1`

### 2. Papago API (네이버)
- **장점**: 한국어 번역 품질 좋음, 무료 할당량 제공
- **단점**: API 키 필요, 무료 할당량 제한
- **설정**: 네이버 개발자 센터에서 API 키 발급

### 3. Google Cloud Translation API
- **장점**: 안정적, 품질 좋음
- **단점**: 유료 (월 50만자 무료 후 과금)
- **설정**: Google Cloud Console에서 API 키 발급

## 사용 방법

### 기본 사용 (googletrans)
```bash
# 모든 영어 리뷰 번역
python translate_reviews.py

# 최대 100개만 번역 (테스트용)
python translate_reviews.py --max-reviews 100

# 번역만 확인하고 저장하지 않음
python translate_reviews.py --dry-run
```

### 특정 영화의 리뷰만 번역
```bash
python translate_reviews.py --movie-id 1
```

### Papago API 사용
```bash
python translate_reviews.py --method papago \
  --papago-id "YOUR_CLIENT_ID" \
  --papago-secret "YOUR_CLIENT_SECRET"
```

### Google Translate API 사용
```bash
python translate_reviews.py --method google_api \
  --google-api-key "YOUR_API_KEY"
```

## 주의사항

1. **기존 content 덮어쓰기**: 기본적으로 번역된 내용으로 `content` 필드를 교체합니다
2. **API 제한**: googletrans는 하루 약 15,000자 제한이 있을 수 있습니다
3. **번역 품질**: 자동 번역이므로 완벽하지 않을 수 있습니다
4. **시간 소요**: 많은 리뷰를 번역하면 시간이 걸립니다

## 대안: 별도 필드에 번역 저장

만약 원문을 유지하고 싶다면 Review 모델에 `kor_content` 필드를 추가할 수 있습니다:

```python
# reviews/models.py에 추가
kor_content = models.TextField(blank=True, help_text="한국어 번역")
```

이 경우 스크립트를 수정하여 `content` 대신 `kor_content`에 저장하도록 변경해야 합니다.

