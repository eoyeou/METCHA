<template>
  <div class="home-container">
    <!-- 헤더 -->
    <header class="home-header">
      <div class="logo" @click="goToHome">MOVIE SITE</div>
      <div class="header-buttons" v-if="authStore.isAuthenticated">
        <button @click="goToProfile" class="btn-header">내 프로필</button>
        <button @click="goToPreference" class="btn-header">리뷰작성</button>
        <button @click="handleLogout" class="btn-header btn-logout">로그아웃</button>
      </div>
      <div class="header-buttons" v-else>
        <button @click="goToLogin" class="btn-header">로그인</button>
        <button @click="goToSignup" class="btn-header">회원가입</button>
      </div>
    </header>

    <!-- 메인 컨텐츠 -->
    <main class="main-content">
      <!-- 검색창 -->
      <div class="search-section">
        <div class="search-box">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            @focus="showResults = true"
            type="text"
            placeholder="영화 제목을 검색하세요..."
            class="search-input"
          >
          <button class="search-btn">🔍</button>
        </div>

        <!-- 검색 결과 (자동완성) -->
        <div v-if="showResults && searchResults.length > 0" class="search-results">
          <div
            v-for="movie in searchResults"
            :key="movie.id"
            @click="goToMovie(movie.id)"
            class="search-result-item"
          >
            <img 
              :src="movie.poster_url || 'https://via.placeholder.com/50x75'" 
              alt="포스터"
              class="result-poster"
            >
            <div class="result-info">
              <p class="result-title">{{ movie.title }}</p>
              <p class="result-year">{{ movie.release_year }}</p>
            </div>
            <div class="result-rating">
              ⭐ {{ movie.avg_rating.toFixed(1) }}
            </div>
          </div>
        </div>

        <!-- 검색 결과 없음 -->
        <div v-if="showResults && searchQuery && searchResults.length === 0" class="no-results">
          검색 결과가 없습니다.
        </div>
      </div>

      <!-- 인기 영화 목록 (검색 안 할 때) -->
      <div v-if="!searchQuery" class="popular-movies">
        <h2>인기 영화</h2>
        <div class="movie-grid">
          <div
            v-for="movie in popularMovies"
            :key="movie.id"
            @click="goToMovie(movie.id)"
            class="movie-card"
          >
            <img 
              :src="movie.poster_url || 'https://via.placeholder.com/200x300'" 
              :alt="movie.title"
              class="movie-poster"
            >
            <div class="movie-info">
              <h3>{{ movie.title }}</h3>
              <p class="movie-year">{{ movie.release_year }}</p>
              <p class="movie-rating">⭐ {{ movie.avg_rating.toFixed(1) }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const popularMovies = ref([])

const API_URL = 'http://127.0.0.1:8000/api'

// 페이지 로드 시 인기 영화 가져오기
onMounted(async () => {
  try {
    const response = await axios.get(`${API_URL}/movies/`)
    popularMovies.value = response.data.slice(0, 12) // 상위 12개만
  } catch (error) {
    console.error('영화 목록 로드 실패:', error)
  }
})

// 검색 처리 (실시간)
let searchTimeout = null
const handleSearch = () => {
  // 디바운싱: 입력 후 300ms 후에 검색
  clearTimeout(searchTimeout)
  
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    showResults.value = false
    return
  }

  searchTimeout = setTimeout(async () => {
    try {
      const response = await axios.get(`${API_URL}/movies/`)
      
      // 제목으로 필터링 (대소문자 구분 없이)
      searchResults.value = response.data.filter(movie =>
        movie.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        movie.original_title?.toLowerCase().includes(searchQuery.value.toLowerCase())
      ).slice(0, 5) // 최대 5개만 표시
      
      showResults.value = true
    } catch (error) {
      console.error('검색 실패:', error)
    }
  }, 300)
}

// 영화 상세 페이지로 이동
const goToMovie = (movieId) => {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
  router.push(`/movies/${movieId}`)
}

// 네비게이션
const goToHome = () => router.push('/')
const goToProfile = () => router.push('/profile')
const goToPreference = () => router.push('/reviews/create')
const goToLogin = () => router.push('/login')
const goToSignup = () => router.push('/register')

// 로그아웃
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

// 검색창 외부 클릭 시 결과 닫기
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-section')) {
      showResults.value = false
    }
  })
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.logo {
  font-size: 28px;
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

.btn-logout {
  background: rgba(231, 76, 60, 0.3);
  border-color: rgba(231, 76, 60, 0.5);
}

.btn-logout:hover {
  background: rgba(231, 76, 60, 0.5);
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* 검색 섹션 */
.search-section {
  position: relative;
  max-width: 800px;
  margin: 0 auto 60px;
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
  border-color: #e94560;
  box-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
}

.search-input {
  flex: 1;
  padding: 20px 30px;
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-btn {
  padding: 20px 30px;
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  transition: transform 0.3s;
}

.search-btn:hover {
  transform: scale(1.1);
}

/* 검색 결과 (자동완성) */
.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 10px;
  background: rgba(30, 30, 46, 0.98);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background: rgba(233, 69, 96, 0.2);
  transform: translateX(5px);
}

.result-poster {
  width: 50px;
  height: 75px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 15px;
}

.result-info {
  flex: 1;
}

.result-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.result-year {
  font-size: 14px;
  color: #aaa;
}

.result-rating {
  font-size: 16px;
  color: #f39c12;
  font-weight: bold;
}

.no-results {
  padding: 30px;
  text-align: center;
  color: #aaa;
  background: rgba(30, 30, 46, 0.98);
  border-radius: 20px;
  margin-top: 10px;
}

/* 인기 영화 그리드 */
.popular-movies h2 {
  font-size: 32px;
  margin-bottom: 30px;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.movie-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.movie-info {
  padding: 15px;
}

.movie-info h3 {
  font-size: 16px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-year {
  font-size: 14px;
  color: #aaa;
  margin-bottom: 5px;
}

.movie-rating {
  font-size: 14px;
  color: #f39c12;
}

/* 반응형 */
@media (max-width: 768px) {
  .main-content {
    padding: 40px 20px;
  }

  .search-section {
    margin-bottom: 40px;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
  }
}
</style>