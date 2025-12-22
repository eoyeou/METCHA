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
          <button @click="goToSearchResults" class="search-btn">🔍</button>
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

      <!-- 영화 섹션들 (검색 안 할 때) -->
      <div v-if="!searchQuery" class="movies-sections">
        <!-- 큰 포스터 카드 (최신 영화) -->
        <div v-if="featuredMovies.length > 0" class="featured-section">
          <h2>신작 영화</h2>
          <div class="featured-movies">
            <div
              v-for="movie in featuredMovies.slice(0, 3)"
              :key="movie.id"
              @click="goToMovie(movie.id)"
              class="featured-card"
              :style="{ backgroundImage: `url(${movie.poster_url || 'https://via.placeholder.com/800x450'})` }"
            >
              <div class="featured-overlay"></div>
              <div class="featured-content">
                <h3>{{ movie.title }}</h3>
                <p class="featured-description">{{ movie.kor_description || movie.description || '줄거리 정보가 없습니다.' }}</p>
                <div class="featured-meta">
                  <span class="featured-year">{{ movie.release_year }}</span>
                  <span class="featured-rating">⭐ {{ movie.avg_rating.toFixed(1) }}</span>
                </div>
                <button class="btn-more-info">더 알아보기</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 인기 영화 슬라이더 -->
        <div class="movie-slider-section">
          <h2>인기 영화</h2>
          <div v-if="popularMovies.length === 0" class="empty-state">
            <p>영화를 불러오는 중...</p>
          </div>
          <div v-else class="movie-slider-container">
            <button 
              @click="scrollSlider('left', 'popular')" 
              class="slider-btn slider-btn-left"
              :disabled="!canScrollLeft"
            >
              ‹
            </button>
            <div 
              ref="sliderRef"
              class="movie-slider"
              @scroll="updateScrollButtons"
            >
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
            <button 
              @click="scrollSlider('right', 'popular')" 
              class="slider-btn slider-btn-right"
              :disabled="!canScrollRight"
            >
              ›
            </button>
          </div>
        </div>

        <!-- 평점 높은 영화 슬라이더 -->
        <div class="movie-slider-section">
          <h2>평점 높은 영화</h2>
          <div v-if="topRatedMovies.length === 0" class="empty-state">
            <p>영화를 불러오는 중...</p>
          </div>
          <div v-else class="movie-slider-container">
            <button 
              @click="scrollSlider('left', 'topRated')" 
              class="slider-btn slider-btn-left"
              :disabled="!canScrollTopRatedLeft"
            >
              ‹
            </button>
            <div 
              ref="topRatedSliderRef"
              class="movie-slider"
              @scroll="updateTopRatedScrollButtons"
            >
              <div
                v-for="movie in topRatedMovies"
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
            <button 
              @click="scrollSlider('right', 'topRated')" 
              class="slider-btn slider-btn-right"
              :disabled="!canScrollTopRatedRight"
            >
              ›
            </button>
          </div>
        </div>

        <!-- 장르별 슬라이더들 -->
        <div v-for="genreSection in genreSections" :key="genreSection.genre" class="movie-slider-section">
          <h2>{{ genreSection.title }}</h2>
          <div v-if="genreSection.movies.length === 0" class="empty-state">
            <p>영화를 불러오는 중...</p>
          </div>
          <div v-else class="movie-slider-container">
            <button 
              @click="scrollSlider('left', genreSection.genre)" 
              class="slider-btn slider-btn-left"
              :disabled="!genreSection.canScrollLeft"
            >
              ‹
            </button>
            <div 
              :ref="el => genreSection.sliderRef = el"
              class="movie-slider"
              @scroll="() => updateGenreScrollButtons(genreSection.genre)"
            >
              <div
                v-for="movie in genreSection.movies"
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
            <button 
              @click="scrollSlider('right', genreSection.genre)" 
              class="slider-btn slider-btn-right"
              :disabled="!genreSection.canScrollRight"
            >
              ›
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const popularMovies = ref([])
const featuredMovies = ref([])
const topRatedMovies = ref([])
const sliderRef = ref(null)
const topRatedSliderRef = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)
const canScrollTopRatedLeft = ref(false)
const canScrollTopRatedRight = ref(true)

// 장르별 슬라이더 데이터 (한국어/영어 모두 지원)
const genreSections = ref([
  { genre: '드라마', title: 'Top 10 드라마 영화', movies: [], sliderRef: null, canScrollLeft: false, canScrollRight: true },
  { genre: '액션', title: 'Top 10 액션 영화', movies: [], sliderRef: null, canScrollLeft: false, canScrollRight: true },
  { genre: '공포', title: 'Top 10 공포 영화', movies: [], sliderRef: null, canScrollLeft: false, canScrollRight: true },
  { genre: '코미디', title: 'Top 10 코미디 영화', movies: [], sliderRef: null, canScrollLeft: false, canScrollRight: true },
])

const API_URL = 'http://127.0.0.1:8000/api'

// 영화 데이터 로드 함수들
const loadPopularMovies = async () => {
  try {
    const response = await axios.get(`${API_URL}/movies/`, {
      params: { order_by: 'reviews' }
    })
    let movies = Array.isArray(response.data) ? response.data : (response.data?.results || [])
    popularMovies.value = movies.slice(0, 12)
    await nextTick()
    updateScrollButtons()
  } catch (error) {
    console.error('인기 영화 로드 실패:', error)
  }
}

const loadFeaturedMovies = async () => {
  try {
    const response = await axios.get(`${API_URL}/movies/`, {
      params: { order_by: '-created_at' }
    })
    let movies = Array.isArray(response.data) ? response.data : (response.data?.results || [])
    featuredMovies.value = movies.slice(0, 3)
  } catch (error) {
    console.error('신작 영화 로드 실패:', error)
  }
}

const loadTopRatedMovies = async () => {
  try {
    const response = await axios.get(`${API_URL}/movies/`, {
      params: { order_by: 'rating' }
    })
    let movies = Array.isArray(response.data) ? response.data : (response.data?.results || [])
    topRatedMovies.value = movies.slice(0, 12)
    await nextTick()
    updateTopRatedScrollButtons()
  } catch (error) {
    console.error('평점 높은 영화 로드 실패:', error)
  }
}

const loadGenreMovies = async (genreSection) => {
  try {
    console.log(`[장르 영화 로드 시작] ${genreSection.title} (장르: ${genreSection.genre})`)
    
    // 먼저 전체 영화 목록 가져오기
    const allMoviesResponse = await axios.get(`${API_URL}/movies/`)
    let allMovies = Array.isArray(allMoviesResponse.data) ? allMoviesResponse.data : (allMoviesResponse.data?.results || [])
    console.log(`[전체 영화] ${allMovies.length}개`)
    
    // 프론트엔드에서 장르 필터링
    // 디버깅: 장르가 있는 영화들 확인
    const moviesWithGenres = allMovies.filter(m => m.genres && m.genres.length > 0)
    const moviesWithoutGenres = allMovies.filter(m => !m.genres || m.genres.length === 0)
    
    console.log(`[디버깅] 전체 영화: ${allMovies.length}개`)
    console.log(`[디버깅] 장르가 있는 영화: ${moviesWithGenres.length}개`)
    console.log(`[디버깅] 장르가 없는 영화: ${moviesWithoutGenres.length}개`)
    
    if (moviesWithGenres.length > 0) {
      const firstMovie = moviesWithGenres[0]
      console.log(`[디버깅] 장르가 있는 첫 번째 영화:`, {
        title: firstMovie.title,
        genres: firstMovie.genres,
        firstGenre: firstMovie.genres[0],
        firstGenreKeys: firstMovie.genres[0] ? Object.keys(firstMovie.genres[0]) : []
      })
      
      // 실제 장르 이름 추출 테스트
      const testGenres = firstMovie.genres.map(g => {
        if (typeof g === 'string') return g
        return g?.genre_name || g?.name || String(g)
      })
      console.log(`[디버깅] 추출된 장르 이름들:`, testGenres)
      
      // 모든 영화의 장르 목록 수집 (중복 제거)
      const allGenreNames = new Set()
      moviesWithGenres.slice(0, 20).forEach(m => {
        m.genres.forEach(g => {
          const genreName = typeof g === 'string' ? g : (g?.genre_name || g?.name)
          if (genreName) allGenreNames.add(genreName)
        })
      })
      console.log(`[디버깅] DB에 있는 장르 목록 (샘플 20개 영화 기준):`, Array.from(allGenreNames).sort())
    }
    
    const filteredMovies = allMovies.filter(movie => {
      if (!movie.genres || !Array.isArray(movie.genres) || movie.genres.length === 0) {
        return false
      }
      
      // 장르 이름 매핑 (한국어/영어 모두) - TMDB 한국어 장르명 포함
      const genreMap = {
        '드라마': ['드라마', 'drama', '드라', '드라마틱'],
        '액션': ['액션', 'action', '액', '액션/어드벤처'],
        '공포': ['공포', 'horror', '호러', '스릴러', 'thriller'],
        '코미디': ['코미디', 'comedy', '코미', '코미디/로맨스'],
      }
      
      const searchTerms = genreMap[genreSection.genre] || [genreSection.genre.toLowerCase()]
      
      // 디버깅: 첫 번째 영화의 장르와 검색어 비교
      if (allMovies.indexOf(movie) === 0 && genreSection.genre === '드라마') {
        console.log(`[디버깅] 첫 번째 영화 필터링 테스트:`, {
          movieTitle: movie.title,
          movieGenres: movie.genres.map(g => typeof g === 'string' ? g : (g?.genre_name || g?.name)),
          searchTerms,
          genreSection: genreSection.genre
        })
      }
      
      // 영화의 장르 이름 추출 (간단하게)
      const movieGenreNames = movie.genres.map(g => {
        if (typeof g === 'string') return g
        if (g && typeof g === 'object') return g.genre_name || g.name || ''
        return ''
      }).filter(name => name && name.trim())
      
      // 대소문자 구분 없이 비교
      const movieGenresLower = movieGenreNames.map(name => name.toLowerCase().trim())
      
      // 검색어와 매칭되는지 확인
      const matches = searchTerms.some(searchTerm => {
        const searchTermLower = searchTerm.toLowerCase().trim()
        return movieGenresLower.some(movieGenre => {
          // 정확히 일치
          if (movieGenre === searchTermLower) return true
          // 포함 관계 확인
          if (movieGenre.includes(searchTermLower) || searchTermLower.includes(movieGenre)) return true
          return false
        })
      })
      
      return matches
    })
    
    // 디버깅: 매칭된 영화들 확인
    if (filteredMovies.length > 0) {
      console.log(`[매칭 성공] ${genreSection.title}:`, filteredMovies.slice(0, 3).map(m => ({
        title: m.title,
        genres: m.genres.map(g => typeof g === 'string' ? g : (g?.genre_name || g?.name))
      })))
    }
    
    console.log(`[장르 필터링 후] ${genreSection.title}: ${filteredMovies.length}개`)
    
    // 디버깅: 필터링이 실패한 경우 샘플 확인
    if (filteredMovies.length === 0 && moviesWithGenres.length > 0) {
      // 장르가 있는 영화 중에서 해당 장르가 있는지 확인
      const sampleMovies = moviesWithGenres.slice(0, 5)
      const genreMap = {
        '드라마': ['드라마', 'drama', '드라', '드라마틱'],
        '액션': ['액션', 'action', '액', '액션/어드벤처'],
        '공포': ['공포', 'horror', '호러', '스릴러', 'thriller'],
        '코미디': ['코미디', 'comedy', '코미', '코미디/로맨스'],
      }
      const searchTerms = genreMap[genreSection.genre] || [genreSection.genre.toLowerCase()]
      
      console.log(`[디버깅] 필터링 실패 - 샘플 영화들:`, {
        searchGenre: genreSection.genre,
        searchTerms,
        sampleMovies: sampleMovies.map(m => ({
          title: m.title,
          genres: m.genres.map(g => typeof g === 'string' ? g : (g?.genre_name || g?.name))
        }))
      })
    }
    
    // 평점순으로 정렬
    const sortedMovies = filteredMovies.sort((a, b) => {
      if (b.avg_rating !== a.avg_rating) {
        return b.avg_rating - a.avg_rating
      }
      return b.review_count - a.review_count
    })
    
    genreSection.movies = sortedMovies.slice(0, 10)
    console.log(`[장르 영화 최종] ${genreSection.title}: ${genreSection.movies.length}개 표시`)
    
    // 디버깅: 첫 번째 영화의 장르 정보 출력
    if (genreSection.movies.length > 0) {
      console.log(`[첫 번째 영화 장르] ${genreSection.movies[0].title}:`, genreSection.movies[0].genres?.map(g => g.genre_name))
    }
    
    await nextTick()
    updateGenreScrollButtons(genreSection.genre)
  } catch (error) {
    console.error(`[장르 영화 로드 실패] ${genreSection.title}:`, error)
    console.error('에러 상세:', error.response?.data || error.message)
    // 에러가 발생해도 빈 배열로 설정하여 UI가 깨지지 않도록
    genreSection.movies = []
  }
}

// 페이지 로드 시 모든 영화 데이터 가져오기
onMounted(async () => {
  await Promise.all([
    loadPopularMovies(),
    loadFeaturedMovies(),
    loadTopRatedMovies(),
    ...genreSections.value.map(section => loadGenreMovies(section))
  ])
})

// 검색 처리 (실시간 자동완성)
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
      // REST Framework pagination이 활성화되어 있으면 results를 사용
      const movies = response.data.results || response.data
      
      // 제목으로 필터링 (대소문자 구분 없이)
      searchResults.value = movies.filter(movie =>
        movie.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        movie.original_title?.toLowerCase().includes(searchQuery.value.toLowerCase())
      ).slice(0, 5) // 최대 5개만 표시
      
      showResults.value = true
    } catch (error) {
      console.error('검색 실패:', error)
    }
  }, 300)
}

// 검색 결과 페이지로 이동
const goToSearchResults = () => {
  if (searchQuery.value.trim()) {
    router.push({ 
      path: '/search', 
      query: { q: searchQuery.value.trim() } 
    })
  }
}

// 영화 상세 페이지로 이동
const goToMovie = (movieId) => {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
  router.push(`/movies/${movieId}`)
}

// 슬라이더 스크롤
const scrollSlider = (direction, type = 'popular') => {
  let targetRef = null
  
  if (type === 'popular') {
    targetRef = sliderRef.value
  } else if (type === 'topRated') {
    targetRef = topRatedSliderRef.value
  } else {
    // 장르별 슬라이더
    const genreSection = genreSections.value.find(s => s.genre === type)
    if (genreSection && genreSection.sliderRef) {
      targetRef = genreSection.sliderRef
    }
  }
  
  if (!targetRef) return
  
  const scrollAmount = 600 // 한 번에 스크롤할 픽셀 수
  const currentScroll = targetRef.scrollLeft
  
  if (direction === 'left') {
    targetRef.scrollTo({
      left: currentScroll - scrollAmount,
      behavior: 'smooth'
    })
  } else {
    targetRef.scrollTo({
      left: currentScroll + scrollAmount,
      behavior: 'smooth'
    })
  }
}

// 스크롤 버튼 상태 업데이트
const updateScrollButtons = () => {
  if (!sliderRef.value) return
  
  const { scrollLeft, scrollWidth, clientWidth } = sliderRef.value
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 10
}

const updateTopRatedScrollButtons = () => {
  if (!topRatedSliderRef.value) return
  
  const { scrollLeft, scrollWidth, clientWidth } = topRatedSliderRef.value
  canScrollTopRatedLeft.value = scrollLeft > 0
  canScrollTopRatedRight.value = scrollLeft < scrollWidth - clientWidth - 10
}

const updateGenreScrollButtons = (genre) => {
  const genreSection = genreSections.value.find(s => s.genre === genre)
  if (!genreSection || !genreSection.sliderRef) return
  
  const { scrollLeft, scrollWidth, clientWidth } = genreSection.sliderRef
  genreSection.canScrollLeft = scrollLeft > 0
  genreSection.canScrollRight = scrollLeft < scrollWidth - clientWidth - 10
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

/* 영화 섹션들 */
.movies-sections {
  display: flex;
  flex-direction: column;
  gap: 60px;
}

.movie-slider-section {
  margin-bottom: 40px;
}

.movie-slider-section h2 {
  font-size: 32px;
  margin-bottom: 30px;
  font-weight: bold;
}

/* 큰 포스터 카드 섹션 */
.featured-section {
  margin-bottom: 60px;
}

.featured-section h2 {
  font-size: 32px;
  margin-bottom: 30px;
  font-weight: bold;
}

.featured-movies {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.featured-card {
  position: relative;
  height: 500px;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.featured-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border-color: rgba(233, 69, 96, 0.5);
}

.featured-card:hover .featured-overlay {
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.85));
}

.featured-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.8));
  transition: all 0.3s;
}

.featured-content {
  position: relative;
  z-index: 2;
  height: 100%;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.featured-content h3 {
  font-size: 36px;
  margin-bottom: 20px;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8);
}

.featured-description {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 25px;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
}

.featured-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  font-size: 18px;
}

.featured-year {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
}

.featured-rating {
  color: #f39c12;
  font-weight: bold;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
}

.btn-more-info {
  padding: 12px 30px;
  background: linear-gradient(135deg, #e94560, #f39c12);
  border: none;
  border-radius: 25px;
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  align-self: flex-start;
}

.btn-more-info:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
}

.movie-slider-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 10px;
}

.movie-slider {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 10px 0;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  flex: 1;
  /* 스크롤바 숨기기 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.movie-slider::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex: 0 0 200px; /* 고정 너비, 축소/확대 불가 */
  min-width: 200px;
  max-width: 200px;
}

.movie-card:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  display: block;
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

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #aaa;
}

.empty-state p {
  margin: 10px 0;
}

/* 슬라이더 버튼 */
.slider-btn {
  width: 60px;
  height: 380px; /* 영화 카드 전체 높이: 포스터(300px) + 정보영역(약80px) */
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.slider-btn:hover:not(:disabled) {
  background: rgba(233, 69, 96, 0.8);
  border-color: #e94560;
  transform: scale(1.1);
}

.slider-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.slider-btn-left {
  margin-right: 10px;
}

.slider-btn-right {
  margin-left: 10px;
}

/* 반응형 */
@media (max-width: 768px) {
  .main-content {
    padding: 40px 20px;
  }

  .search-section {
    margin-bottom: 40px;
  }

  .featured-movies {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .featured-card {
    height: 400px;
  }

  .featured-content {
    padding: 30px 20px;
  }

  .featured-content h3 {
    font-size: 28px;
  }

  .featured-description {
    -webkit-line-clamp: 3;
    line-clamp: 3;
    font-size: 14px;
  }

  .movie-slider-section h2,
  .featured-section h2 {
    font-size: 24px;
  }

  .movie-card {
    flex: 0 0 150px;
    min-width: 150px;
    max-width: 150px;
  }
  
  .slider-btn {
    width: 50px;
    height: 285px; /* 모바일 영화 카드 전체 높이: 포스터(225px) + 정보영역(약60px) */
    font-size: 30px;
  }
}
</style>