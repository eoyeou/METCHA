# 검색 중복 제거 로직 분석

## 문제 상황

과거에는 영화 이름 그대로 검색했을 때 해당 영화가 순위에서 밀렸던 문제가 있었습니다.
- **원인**: 같은 영화의 여러 리뷰가 각각 별도 항목으로 처리되어 중복 제거 과정에서 순위가 밀림
- **해결**: 중복 제거 로직을 개선하여 같은 영화의 여러 리뷰 중 최고 점수만 유지하도록 변경

## 현재 코드 (개선된 버전)

```python
# 7. 결과 정렬 (영화별로 최고 점수만 유지)
movie_scores = {}  # movie_id -> 최고 점수 정보

for review in similar_reviews:
    movie_id = review_to_movie.get(review['review_id'])
    if not movie_id or movie_id not in movie_dict:
        continue
    
    # ... 점수 계산 ...
    final_score = ...
    
    # 같은 영화의 여러 리뷰 중 최고 점수만 유지
    if movie_id not in movie_scores or final_score > movie_scores[movie_id]['final_score']:
        movie_scores[movie_id] = {
            'movie': movie,
            'similarity': similarity,
            'final_score': final_score,
            'review_id': review['review_id']
        }

# 8. 최종 점수로 정렬
results = list(movie_scores.values())
results.sort(key=lambda x: x['final_score'], reverse=True)
```

### 현재 로직의 장점
- ✅ **최고 점수 보장**: 같은 영화의 여러 리뷰 중 가장 높은 점수만 유지
- ✅ **순서 보장**: 모든 리뷰를 처리한 후 최종 점수로 정렬하므로 정확한 순위 반영
- ✅ **중복 없음**: `movie_scores` 딕셔너리를 사용하여 각 영화당 하나의 항목만 유지

## 과거에 문제가 있었을 가능성이 높은 코드 패턴들

### 패턴 1: 순차 추가 + 첫 항목 우선 중복 제거

```python
# ❌ 문제가 있는 코드 패턴
results = []
seen_movies = set()

for review in similar_reviews:
    movie_id = review_to_movie.get(review['review_id'])
    if movie_id not in seen_movies:  # 첫 번째 리뷰만 추가
        final_score = ...  # 점수 계산
        results.append({
            'movie': movie_dict[movie_id],
            'final_score': final_score
        })
        seen_movies.add(movie_id)

# 점수로 정렬
results.sort(key=lambda x: x['final_score'], reverse=True)
```

**문제점**:
- 같은 영화의 여러 리뷰 중 **첫 번째 리뷰의 점수만** 사용됨
- 첫 번째 리뷰가 낮은 점수를 받고, 나중에 높은 점수의 리뷰가 나와도 이미 추가되어 무시됨
- 예: "매트릭스" 검색 시 첫 리뷰 점수=0.6, 두 번째 리뷰 점수=0.95 → 0.6만 사용되어 순위 하락

### 패턴 2: 모든 리뷰 추가 후 set()으로 중복 제거

```python
# ❌ 문제가 있는 코드 패턴
results = []

for review in similar_reviews:
    movie_id = review_to_movie.get(review['review_id'])
    final_score = ...
    results.append({
        'movie_id': movie_id,
        'movie': movie_dict[movie_id],
        'final_score': final_score
    })

# 중복 제거 (순서 보장 안됨!)
seen = set()
unique_results = []
for r in results:
    if r['movie_id'] not in seen:
        unique_results.append(r)
        seen.add(r['movie_id'])

# 점수로 정렬
unique_results.sort(key=lambda x: x['final_score'], reverse=True)
```

**문제점**:
- 모든 리뷰를 추가한 후 중복 제거하지만, **첫 번째 항목만 유지**되므로 문제는 동일
- 만약 `list(set())`을 사용했다면 순서가 완전히 무작위가 되어 더 큰 문제 발생

### 패턴 3: 리스트에 모두 추가 후 마지막에 딕셔너리로 중복 제거 (최신만 유지)

```python
# ❌ 문제가 있는 코드 패턴
results = []

for review in similar_reviews:
    movie_id = review_to_movie.get(review['review_id'])
    final_score = ...
    results.append({
        'movie_id': movie_id,
        'movie': movie_dict[movie_id],
        'final_score': final_score
    })

# 중복 제거 (마지막 항목만 유지)
movie_dict_final = {}
for r in results:
    movie_dict_final[r['movie_id']] = r  # 마지막 항목이 덮어씀

unique_results = list(movie_dict_final.values())
unique_results.sort(key=lambda x: x['final_score'], reverse=True)
```

**문제점**:
- 마지막 항목만 유지되는데, 이게 항상 최고 점수는 아님
- `similar_reviews`의 순서에 따라 결과가 달라짐

## 핵심 차이점

### 과거 문제 코드의 특징
1. **점수 비교 없음**: 중복 제거 시 점수를 비교하지 않고 단순히 첫 번째 또는 마지막 항목만 유지
2. **순서 의존성**: `similar_reviews`의 순서에 따라 결과가 달라짐
3. **최적화 부족**: 같은 영화의 여러 리뷰를 모두 처리하지만 최고 점수를 선택하지 않음

### 현재 개선 코드의 특징
1. **점수 비교**: `final_score > movie_scores[movie_id]['final_score']` 조건으로 항상 최고 점수 유지
2. **순서 독립성**: `similar_reviews`의 순서와 무관하게 항상 최고 점수 선택
3. **명확한 로직**: "같은 영화의 여러 리뷰 중 최고 점수만 유지"라는 의도가 명확히 드러남

## 결론

과거 문제의 핵심은 **중복 제거 시점과 방식**이었습니다:
- ❌ **과거**: 리뷰를 순차적으로 처리하면서 처음 나온 리뷰의 점수만 사용
- ✅ **현재**: 모든 리뷰를 처리하면서 점수를 비교하여 최고 점수만 유지

이로 인해 같은 영화의 여러 리뷰가 있을 때, 첫 번째 리뷰의 점수가 낮으면 해당 영화의 순위가 밀렸던 것입니다.
