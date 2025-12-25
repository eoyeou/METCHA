<template>
  <div class="search-results-page">
    <div class="search-header">
      <div class="header-left">
        <div class="logo" @click="goToHome">METCHA</div>
        <div class="search-box-container">
          <div class="search-box">
            <input
              v-model="searchQuery"
              @keyup.enter="performSearch"
              @input="handleSearchInput"
              type="text"
              placeholder="영화 제목으로 검색..."
              class="search-input"
            />
            <button @click="performSearch" class="search-btn">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5" fill="none"/>
                <path d="m14 14 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-nav" @click="goToHome">홈</button>
        <button class="btn-nav" @click="goToProfile">프로필</button>
        <button class="btn-nav" @click="goToReviewCreate">리뷰작성</button>
        <button 
          v-if="authStore.isAuthenticated"
          class="btn-nav btn-logout" 
          @click="handleLogout"
        >
          로그아웃
        </button>
        <button 
          v-else
          class="btn-nav" 
          @click="goToLogin"
        >
          로그인
        </button>
      </div>
    </div>

    <div class="search-content">
      <div v-if="!searchQuery && !routeQuery" class="empty-search">
        <h2>검색어를 입력해주세요</h2>
        <p>영화 제목이나 원제로 검색할 수 있습니다.</p>
      </div>

      <div v-else class="results-section">
        <div class="results-header">
          <h2>
            <span v-if="isLoading">검색 중...</span>
            <span v-else>
              "{{ displayQuery }}" 검색 결과 ({{ searchResults.length }}개)
            </span>
          </h2>
        </div>

        <div v-if="isLoading" class="loading-state">
          <p>영화를 검색하는 중...</p>
        </div>

        <div v-else-if="searchResults.length === 0" class="no-results">
          <p>검색 결과가 없습니다.</p>
          <p class="no-results-hint">다른 키워드로 검색해보세요.</p>
        </div>

        <div v-else class="movies-grid">
          <div
            v-for="movie in searchResults"
            :key="movie.id"
            @click="goToMovie(movie.id)"
            class="movie-card"
          >
            <div class="movie-poster-wrapper">
              <img 
                :src="movie.poster_url || 'https://via.placeholder.com/200x300'" 
                :alt="movie.title"
                class="movie-poster"
              />
            </div>
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <p v-if="movie.original_title" class="movie-original-title">{{ movie.original_title }}</p>
              <div class="movie-meta">
                <span class="movie-year">{{ movie.release_year }}</span>
                <span class="movie-rating">⭐ {{ movie.avg_rating.toFixed(1) }}</span>
              </div>
              <div v-if="movie.genres && movie.genres.length > 0" class="movie-genres">
                <span 
                  v-for="genre in movie.genres.slice(0, 3)" 
                  :key="genre.id"
                  class="genre-tag"
                >
                  {{ genre.genre_name }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const searchQuery = ref('')
const searchResults = ref([])
const isLoading = ref(false)
const routeQuery = ref('')

const API_URL = 'http://127.0.0.1:8000/api'

// URL 쿼리 파라미터에서 검색어 가져오기
onMounted(() => {
  const query = route.query.q
  if (query) {
    routeQuery.value = query
    searchQuery.value = query
    performSearch()
  }
})

// 라우트 쿼리 파라미터 변경 감지 (뒤로가기/앞으로가기 등)
watch(() => route.query.q, (newQuery) => {
  if (newQuery && newQuery !== searchQuery.value) {
    routeQuery.value = newQuery
    searchQuery.value = newQuery
    performSearch()
  } else if (!newQuery && searchQuery.value) {
    // URL에서 쿼리가 제거되면 검색어도 초기화
    searchQuery.value = ''
    routeQuery.value = ''
    searchResults.value = []
  }
})


// 표시용 검색어 (현재 입력 중인 검색어 우선, 없으면 URL 쿼리)
const displayQuery = computed(() => {
  return searchQuery.value.trim() || routeQuery.value
})

// 검색 실행 (ChromaDB 기반 의미 검색)
const performSearch = async () => {
  const query = searchQuery.value.trim()
  if (!query) {
    searchResults.value = []
    return
  }

  isLoading.value = true
  try {
    // ChromaDB 기반 의미 검색 API 호출
    const response = await axios.post(`${API_URL}/movies/search/semantic/`, {
      query: query,
      limit: 20
    })
    
    searchResults.value = response.data.results || []
    routeQuery.value = query
    
    // URL 업데이트 (검색어를 쿼리 파라미터로)
    if (route.query.q !== query) {
      router.push({ 
        path: '/search', 
        query: { q: query } 
      })
    }
  } catch (error) {
    console.error('검색 실패:', error)
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

// 검색 입력 처리 (디바운싱)
let searchTimeout = null
const handleSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      // URL 업데이트 및 검색 실행
      router.push({ 
        path: '/search', 
        query: { q: searchQuery.value.trim() } 
      })
      performSearch()
    } else {
      // 검색어가 비어있으면 URL에서 쿼리 제거
      router.push({ path: '/search' })
      searchResults.value = []
    }
  }, 500)
}

// 검색어 변경 감지하여 자동 검색
watch(searchQuery, (newValue) => {
  if (newValue.trim() && newValue !== routeQuery.value) {
    handleSearchInput()
  }
})

// 영화 상세 페이지로 이동
const goToMovie = (movieId) => {
  router.push(`/movies/${movieId}`)
}

// 네비게이션
const goToHome = () => router.push('/')
const goToProfile = () => router.push('/profile')
const goToReviewCreate = () => router.push('/reviews/create')
const goToLogin = () => router.push('/login')

// 로그아웃
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}
</script>

<style scoped>
.search-results-page {
  min-height: 100vh;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
  flex: 1;
}

.logo {
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: -2px;
  font-size: 1.5rem;
  cursor: none;
  color: var(--text-primary);
}

.search-box-container {
  flex: 1;
  max-width: 600px;
}

.search-box {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
}

.search-box:focus-within {
  border-color: #555;
  box-shadow: 0 0 20px rgba(204, 255, 0, 0.3);
}

.search-input {
  flex: 1;
  padding: 15px 25px;
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-btn {
  padding: 15px 0 15px 20px;
  background: transparent;
  border: none;
  cursor: none;
  color: var(--text-primary);
  transition: all 0.3s;
  opacity: 0.4;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn svg {
  width: 18px;
  height: 18px;
  transition: all 0.3s;
}

.search-box:focus-within .search-btn {
  opacity: 1;
  color: var(--accent-acid);
}

.search-btn:hover {
  opacity: 1;
  color: var(--accent-acid);
}

.search-btn:hover svg {
  transform: scale(1.1);
}

.header-right {
  display: flex;
  gap: 15px;
}

.btn-nav {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.btn-nav:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-logout {
  background: rgba(231, 76, 60, 0.3);
  border-color: rgba(231, 76, 60, 0.5);
}

.btn-logout:hover {
  background: rgba(231, 76, 60, 0.5);
}

.search-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

.empty-search {
  text-align: center;
  padding: 100px 20px;
}

.empty-search h2 {
  font-size: 32px;
  margin-bottom: 15px;
}

.empty-search p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
}

.results-section {
  margin-top: 20px;
}

.results-header {
  margin-bottom: 40px;
}

.results-header h2 {
  font-size: 32px;
  font-weight: bold;
}

.loading-state,
.no-results {
  text-align: center;
  padding: 100px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.no-results-hint {
  margin-top: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.movie-card:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
  border-color: #555;
}

.movie-poster-wrapper {
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.movie-info {
  padding: 15px;
}

.movie-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-original-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
}

.movie-year {
  color: rgba(255, 255, 255, 0.7);
}

.movie-rating {
  color: #f39c12;
  font-weight: bold;
}

.movie-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.genre-tag {
  padding: 3px 8px;
  background: rgba(204, 255, 0, 0.1);
  border: 1px solid var(--accent-acid);
  border-radius: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
}

/* 반응형 */
@media (max-width: 768px) {
  .search-header {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
  }

  .header-left {
    width: 100%;
    flex-direction: column;
    gap: 15px;
  }

  .search-box-container {
    max-width: 100%;
    width: 100%;
  }

  .header-right {
    flex-wrap: wrap;
    justify-content: center;
  }

  .search-content {
    padding: 40px 20px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
  }

  .results-header h2 {
    font-size: 24px;
  }
}
</style>

