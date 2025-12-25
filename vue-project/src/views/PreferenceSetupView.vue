<template>
  <div class="preference-setup-page">
    <div class="preference-container">
      <h1>취향 설정</h1>
      <p class="subtitle">좋아하는 영화를 최소 3개 이상 선택해주세요</p>

      <!-- 영화 선택 섹션 -->
      <section class="preference-section">
        <div class="selection-info">
          <p class="selection-count">선택한 영화: <strong>{{ selectedMovies.length }}</strong> / 최소 3개</p>
        </div>
        <div class="movie-grid">
          <div
            v-for="movie in availableMovies"
            :key="movie.id"
            @click="toggleMovie(movie.id)"
            :class="['movie-card', { selected: selectedMovies.includes(movie.id) }]"
          >
            <div class="movie-poster-wrapper">
              <img 
                :src="movie.poster_url || 'https://via.placeholder.com/200x300?text=No+Image'" 
                :alt="movie.title"
                class="movie-poster"
              />
              <div v-if="selectedMovies.includes(movie.id)" class="selected-overlay">
                <span class="check-icon">✓</span>
              </div>
            </div>
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <p class="movie-rating">⭐ {{ movie.avg_rating?.toFixed(1) || '0.0' }}</p>
            </div>
          </div>
        </div>
      </section>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="button-group">
        <button @click="skipSetup" class="btn-skip">건너뛰기</button>
        <button 
          @click="savePreferences" 
          class="btn-save" 
          :disabled="isLoading || selectedMovies.length < 3"
        >
          {{ isLoading ? '저장 중...' : '저장하기' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const API_URL = 'http://127.0.0.1:8000/api'

const availableMovies = ref([])
const selectedMovies = ref([])
const error = ref('')
const isLoading = ref(false)

// 영화 토글
const toggleMovie = (movieId) => {
  const index = selectedMovies.value.indexOf(movieId)
  if (index > -1) {
    selectedMovies.value.splice(index, 1)
  } else {
    selectedMovies.value.push(movieId)
  }
}

// 취향 설정 저장
const savePreferences = async () => {
  if (selectedMovies.value.length < 3) {
    error.value = '최소 3개 이상의 영화를 선택해주세요.'
    return
  }

  error.value = ''
  isLoading.value = true

  try {
    await axios.post(
      `${API_URL}/accounts/preferences/`,
      {
        movie_ids: selectedMovies.value
      },
      {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      }
    )
    
    // 홈으로 이동
    router.push('/')
  } catch (err) {
    console.error('취향 설정 저장 실패:', err)
    error.value = err.response?.data?.error || err.response?.data?.detail || '취향 설정 저장에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}

// 건너뛰기
const skipSetup = () => {
  router.push('/')
}

// 영화 목록 가져오기
onMounted(async () => {
  try {
    const response = await axios.get(
      `${API_URL}/accounts/preferences/`,
      {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      }
    )
    
    availableMovies.value = response.data.available_movies || []
    
    // 이미 설정된 선호 영화가 있으면 불러오기
    if (response.data.preferred_movies) {
      selectedMovies.value = response.data.preferred_movies.map(m => m.id)
    }
  } catch (err) {
    console.error('취향 정보 가져오기 실패:', err)
    // 인증 오류인 경우 로그인 페이지로 리다이렉트
    if (err.response?.status === 401) {
      router.push('/login')
      return
    }
    // 영화 목록은 빈 배열로 시작
    availableMovies.value = []
  }
})
</script>

<style scoped>
.preference-setup-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  color: var(--text-primary);
  padding: 40px 20px;
}

.preference-container {
  width: 100%;
  max-width: 1200px;
  background: transparent;
  padding: 60px 40px;
  border: 1px solid #222;
}

h1 {
  font-family: var(--font-display);
  text-align: center;
  margin-bottom: 20px;
  color: var(--text-primary);
  font-size: 3rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -2px;
  line-height: 0.9;
}

.subtitle {
  text-align: center;
  margin-bottom: 40px;
  color: #aaa;
  font-size: 1rem;
  font-family: var(--font-kr);
}

.preference-section {
  margin-bottom: 60px;
}

.selection-info {
  margin-bottom: 30px;
  text-align: center;
}

.selection-count {
  color: #aaa;
  font-size: 1rem;
  font-family: var(--font-kr);
}

.selection-count strong {
  color: var(--accent-acid);
  font-weight: 700;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 30px;
  margin-bottom: 0;
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #333;
  background: transparent;
  overflow: hidden;
  position: relative;
}

.movie-card:hover {
  transform: translateY(-5px);
  border-color: var(--accent-acid);
  box-shadow: 0 5px 20px rgba(204, 255, 0, 0.2);
}

.movie-card.selected {
  border-color: var(--accent-acid);
  box-shadow: 0 0 20px rgba(204, 255, 0, 0.4);
}

.movie-poster-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: grayscale(30%) contrast(110%);
  transition: filter 0.3s;
}

.movie-card:hover .movie-poster,
.movie-card.selected .movie-poster {
  filter: grayscale(0%) contrast(120%);
}

.selected-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(204, 255, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
}

.check-icon {
  font-size: 3rem;
  color: var(--accent-acid);
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.8);
}

.movie-info {
  padding: 15px;
  text-align: center;
}

.movie-title {
  font-family: var(--font-kr);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-rating {
  font-size: 0.85rem;
  color: var(--accent-acid);
  font-family: var(--font-mono);
}

.error-message {
  text-align: center;
  color: #ff4444;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.button-group {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 60px;
  padding-top: 40px;
  border-top: 1px solid #222;
}

.btn-skip,
.btn-save {
  padding: 15px 40px;
  font-family: var(--font-display);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 0;
  border: 1px solid #333;
}

.btn-skip {
  background: transparent;
  color: #666;
}

.btn-skip:hover {
  border-color: #666;
  background: rgba(255, 255, 255, 0.05);
}

.btn-save {
  background: var(--accent-acid);
  color: #000;
  border-color: var(--accent-acid);
  font-weight: 700;
}

.btn-save:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(204, 255, 0, 0.4);
  transform: translateY(-2px);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #333;
  border-color: #333;
  color: #666;
}

/* 반응형 */
@media (max-width: 768px) {
  .preference-container {
    padding: 40px 20px;
  }

  h1 {
    font-size: 2rem;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 20px;
  }

  .button-group {
    flex-direction: column;
  }

  .btn-skip,
  .btn-save {
    width: 100%;
  }
}
</style>
