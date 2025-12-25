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
  background: #000;
  color: #fff;
}

.search-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: var(--bg-color);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #222;
  z-index: 1000;
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
  cursor: pointer;
  color: var(--text-primary);
  text-transform: uppercase;
}

.search-box-container {
  flex: 1;
  max-width: 600px;
}

.search-box {
  display: flex;
  align-items: center;
  background: transparent;
  border-radius: 0;
  overflow: visible;
  border: none;
  border-bottom: 2px solid #333;
  transition: all 0.3s;
}

.search-box:focus-within {
  border-bottom-color: var(--accent-acid);
}

.search-input {
  flex: 1;
  padding: 15px 0;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  font-family: var(--font-mono);
  font-weight: 300;
  letter-spacing: 0.05em;
  outline: none;
  text-align: left;
}

.search-input::placeholder {
  color: #333;
  -webkit-text-stroke: 1px #333;
  color: transparent;
}

.search-btn {
  padding: 15px 0 15px 20px;
  background: transparent;
  border: none;
  cursor: pointer;
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
  background: transparent;
  border: 1px solid #333;
  color: var(--text-primary);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-nav:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--accent-acid);
  color: var(--accent-acid);
}

.btn-logout {
  background: transparent;
  border-color: #666;
  color: #666;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: #999;
  color: #999;
}

.search-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
  padding-top: 180px;
}

.empty-search {
  text-align: center;
  padding: 100px 20px;
}

.empty-search h2 {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.04em;
  margin-bottom: 15px;
  color: var(--text-primary);
}

.empty-search p {
  font-size: 18px;
  font-family: var(--font-kr);
  color: #aaa;
}

.results-section {
  margin-top: 20px;
}

.results-header {
  margin-bottom: 40px;
}

.results-header h2 {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.04em;
  color: var(--text-primary);
  line-height: 0.75;
  font-stretch: condensed;
}

.loading-state,
.no-results {
  text-align: center;
  padding: 100px 20px;
  color: #aaa;
  font-family: var(--font-kr);
}

.no-results-hint {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
  font-family: var(--font-mono);
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

.movie-card {
  cursor: pointer;
  transition: all 0.5s;
  border-radius: 0;
  overflow: hidden;
  background: transparent;
  border: 1px solid #333;
  position: relative;
}

.movie-card:hover {
  transform: scale(1.05) skewX(-2deg);
  border-color: var(--accent-acid);
  box-shadow: 0 0 15px rgba(204, 255, 0, 0.3);
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
  filter: grayscale(30%) contrast(110%);
  transition: 0.5s;
}

.movie-card:hover .movie-poster {
  filter: grayscale(0%) contrast(120%);
  box-shadow: 0 0 20px rgba(204, 255, 0, 0.2);
}

.movie-info {
  padding: 15px;
}

.movie-title {
  font-size: 14px;
  font-family: var(--font-kr);
  font-weight: 500;
  letter-spacing: -0.01em;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
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
  font-size: 12px;
  font-family: var(--font-mono);
  font-weight: 300;
  letter-spacing: 0.05em;
  color: #aaa;
  margin-bottom: 5px;
}

.movie-rating {
  font-size: 14px;
  color: var(--accent-acid);
  font-weight: 500;
}

.movie-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.genre-tag {
  padding: 3px 8px;
  background: transparent;
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--accent-acid);
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
    padding-top: 160px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
  }

  .results-header h2 {
    font-size: 1.8rem;
  }
}
</style>

