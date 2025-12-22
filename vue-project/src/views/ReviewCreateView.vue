<template>
  <div class="review-create-container">
    <!-- 헤더 -->
    <header class="review-header">
      <div class="logo" @click="goToHome">MOVIE SITE</div>
      <div class="header-buttons">
        <button @click="goToProfile" class="btn-header">내 프로필</button>
        <button @click="goToHome" class="btn-header">홈으로</button>
      </div>
    </header>

    <!-- 메인 컨텐츠 -->
    <main class="review-main">
      <div class="review-form-container">
        <h1 class="page-title">리뷰 작성</h1>

        <!-- 로딩 중 -->
        <div v-if="isLoading" class="loading">
          <div class="spinner"></div>
          <p>영화 정보를 불러오는 중...</p>
        </div>

        <!-- 리뷰 작성 폼 -->
        <form v-else @submit.prevent="submitReview" class="review-form">
          
          <!-- 영화 선택 섹션 -->
          <div class="form-section">
            <label class="form-label">영화</label>
            
            <!-- 케이스 1: 영화가 이미 선택된 경우 (상세 페이지에서 온 경우) -->
            <div v-if="movieId && selectedMovie" class="selected-movie-box">
              <img 
                :src="selectedMovie.poster_url || 'https://via.placeholder.com/80x120'" 
                :alt="selectedMovie.title"
                class="selected-movie-poster"
              >
              <div class="selected-movie-info">
                <h3>{{ selectedMovie.title }}</h3>
                <p>{{ selectedMovie.release_year }}</p>
              </div>
            </div>

            <!-- 케이스 2: 영화를 검색해야 하는 경우 (직접 접속) -->
            <div v-else class="movie-search-wrapper">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                @focus="showSearchResults = true"
                type="text"
                placeholder="영화 제목을 검색하세요..."
                class="form-input movie-search"
              >
              
              <!-- 검색 결과 드롭다운 -->
              <div v-if="showSearchResults && searchResults.length > 0" class="search-dropdown">
                <div
                  v-for="result in searchResults"
                  :key="result.id"
                  @click="selectMovie(result)"
                  class="search-result-item"
                >
                  <img 
                    :src="result.poster_url || 'https://via.placeholder.com/40x60'" 
                    alt="포스터"
                    class="result-poster-tiny"
                  >
                  <div class="result-text">
                    <span class="result-title">{{ result.title }}</span>
                    <span class="result-year">{{ result.release_year }}</span>
                  </div>
                </div>
              </div>

              <!-- 검색 결과 없음 -->
              <div v-if="showSearchResults && searchQuery && searchResults.length === 0" class="no-search-results">
                검색 결과가 없습니다.
              </div>

              <!-- 영화를 선택하라는 안내 -->
              <div v-if="!selectedMovie" class="search-hint">
                영화를 검색하고 선택해주세요
              </div>
            </div>
          </div>

          <!-- 별점 (영화 선택 후에만 표시) -->
          <div v-if="selectedMovie" class="form-section">
            <label class="form-label">별점</label>
            <div class="star-rating">
              <button
                v-for="star in 5"
                :key="star"
                type="button"
                @click="setRating(star)"
                @mouseenter="hoverRating = star"
                @mouseleave="hoverRating = 0"
                class="star-button"
              >
                <span class="star" :class="getStarClass(star)">
                  {{ (hoverRating >= star || rating >= star) ? '★' : '☆' }}
                </span>
              </button>
            </div>
            <p class="rating-text">{{ rating }}점</p>
          </div>

          <!-- 리뷰 내용 (영화 선택 후에만 표시) -->
          <div v-if="selectedMovie" class="form-section">
            <label class="form-label">리뷰</label>
            <textarea
              v-model="content"
              rows="10"
              placeholder="영화에 대한 솔직한 리뷰를 작성해주세요"
              class="form-textarea"
              required
            ></textarea>
            <div class="char-count">{{ content.length }} / 1000자</div>
          </div>

          <!-- 스포일러 여부 (영화 선택 후에만 표시) -->
          <div v-if="selectedMovie" class="form-section">
            <label class="checkbox-label">
              <input type="checkbox" v-model="isSpoiler" class="checkbox-input">
              <span>스포일러 포함</span>
            </label>
          </div>

          <!-- 에러 메시지 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <!-- 제출 버튼 (영화 선택 후에만 표시) -->
          <div v-if="selectedMovie" class="form-actions">
            <button type="submit" class="btn-submit" :disabled="!canSubmit">
              리뷰 등록
            </button>
            <button type="button" @click="goBack" class="btn-cancel">
              취소
            </button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const API_URL = 'http://127.0.0.1:8000/api'

// 데이터
const movieId = ref(route.query.movieId || null)
const selectedMovie = ref(null)
const searchQuery = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const rating = ref(0)
const hoverRating = ref(0)
const content = ref('')
const isSpoiler = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

// 영화 정보 로드 (URL에 movieId가 있는 경우)
onMounted(async () => {
  if (movieId.value) {
    isLoading.value = true
    try {
      const response = await axios.get(`${API_URL}/movies/${movieId.value}/`)
      selectedMovie.value = response.data
    } catch (error) {
      console.error('영화 정보 로드 실패:', error)
      errorMessage.value = '영화 정보를 불러오는데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // 외부 클릭 시 검색 결과 닫기
  document.addEventListener('click', handleClickOutside)
})

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 영화 검색
let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  searchTimeout = setTimeout(async () => {
    try {
      const response = await axios.get(`${API_URL}/movies/`)
      // REST Framework pagination이 활성화되어 있으면 results를 사용
      const movies = response.data.results || response.data
      searchResults.value = movies
        .filter(m => 
          m.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          m.original_title?.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
        .slice(0, 8) // 최대 8개
    } catch (error) {
      console.error('영화 검색 실패:', error)
    }
  }, 300)
}

// 영화 선택
const selectMovie = (movieData) => {
  selectedMovie.value = movieData
  movieId.value = movieData.id
  searchQuery.value = ''
  searchResults.value = []
  showSearchResults.value = false
}

// 외부 클릭 감지
const handleClickOutside = (e) => {
  if (!e.target.closest('.movie-search-wrapper')) {
    showSearchResults.value = false
  }
}

// 별점 설정
const setRating = (star) => {
  rating.value = star
}

// 별 클래스
const getStarClass = (star) => {
  const currentRating = hoverRating.value || rating.value
  return {
    'star-filled': star <= currentRating,
    'star-empty': star > currentRating
  }
}

// 제출 가능 여부
const canSubmit = computed(() => {
  return selectedMovie.value && rating.value > 0 && content.value.trim().length > 0
})

// 리뷰 제출
const submitReview = async () => {
  if (!canSubmit.value) {
    errorMessage.value = '모든 필수 항목을 입력해주세요.'
    return
  }

  try {
    const reviewData = {
      movie: selectedMovie.value.id,
      rating: rating.value,
      content: content.value,
      is_spoiler: isSpoiler.value
    }

    await axios.post(`${API_URL}/reviews/`, reviewData)
    
    alert('리뷰가 등록되었습니다!')
    
    // 영화 상세 페이지로 이동
    router.push(`/movies/${selectedMovie.value.id}`)
  } catch (error) {
    console.error('리뷰 등록 실패:', error)
    errorMessage.value = error.response?.data?.detail || '리뷰 등록에 실패했습니다.'
  }
}

// 네비게이션
const goBack = () => {
  if (movieId.value) {
    router.push(`/movies/${movieId.value}`)
  } else {
    router.push('/')
  }
}

const goToHome = () => router.push('/')
const goToProfile = () => router.push('/profile')
</script>

<style scoped>
.review-create-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

/* 헤더 */
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.logo {
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  background: linear-gradient(45deg, #e94560, #f39c12);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-buttons {
  display: flex;
  gap: 15px;
}

.btn-header {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-header:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

/* 메인 */
.review-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.review-form-container {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title {
  font-size: 32px;
  margin-bottom: 30px;
  text-align: center;
}

/* 선택된 영화 박스 (상세 페이지에서 온 경우) */
.selected-movie-box {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(233, 69, 96, 0.1);
  border: 2px solid #e94560;
  border-radius: 15px;
  margin-bottom: 10px;
}

.selected-movie-poster {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.selected-movie-info h3 {
  font-size: 22px;
  margin-bottom: 8px;
  color: #fff;
}

.selected-movie-info p {
  color: #aaa;
  font-size: 16px;
}

/* 로딩 */
.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.1);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 폼 섹션 */
.form-section {
  margin-bottom: 30px;
}

.form-label {
  display: block;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #fff;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 16px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #e94560;
  background: rgba(255, 255, 255, 0.15);
}

/* 영화 검색 */
.movie-search-wrapper {
  position: relative;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 5px;
  background: rgba(30, 30, 46, 0.98);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.search-result-item:hover {
  background: rgba(233, 69, 96, 0.2);
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-poster-tiny {
  width: 40px;
  height: 60px;
  object-fit: cover;
  border-radius: 5px;
  margin-right: 12px;
}

.result-text {
  display: flex;
  flex-direction: column;
}

.result-title {
  font-size: 15px;
  font-weight: bold;
}

.result-year {
  font-size: 13px;
  color: #aaa;
}

.no-search-results {
  padding: 20px;
  text-align: center;
  color: #aaa;
  background: rgba(30, 30, 46, 0.98);
  border-radius: 10px;
  margin-top: 5px;
}

.search-hint {
  margin-top: 10px;
  padding: 15px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 10px;
  color: #ffc107;
  text-align: center;
  font-size: 14px;
}

/* 별점 */
.star-rating {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.star-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s;
}

.star-button:hover {
  transform: scale(1.2);
}

.star {
  font-size: 48px;
  transition: all 0.2s;
}

.star-filled {
  color: #f39c12;
}

.star-empty {
  color: rgba(255, 255, 255, 0.3);
}

.rating-text {
  font-size: 18px;
  color: #f39c12;
  font-weight: bold;
}

/* 텍스트 영역 */
.form-textarea {
  width: 100%;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s;
}

.form-textarea:focus {
  outline: none;
  border-color: #e94560;
  background: rgba(255, 255, 255, 0.15);
}

.char-count {
  text-align: right;
  font-size: 14px;
  color: #aaa;
  margin-top: 8px;
}

/* 체크박스 */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 16px;
}

.checkbox-input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

/* 에러 메시지 */
.error-message {
  padding: 15px;
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid #e74c3c;
  border-radius: 10px;
  color: #ff6b6b;
  margin-bottom: 20px;
  text-align: center;
}

/* 버튼 */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-submit,
.btn-cancel {
  flex: 1;
  padding: 15px 30px;
  border: none;
  border-radius: 10px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit {
  background: linear-gradient(135deg, #e94560 0%, #f39c12 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 반응형 */
@media (max-width: 768px) {
  .review-form-container {
    padding: 30px 20px;
  }

  .page-title {
    font-size: 24px;
  }

  .selected-movie-box {
    flex-direction: column;
    text-align: center;
  }

  .star {
    font-size: 36px;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>