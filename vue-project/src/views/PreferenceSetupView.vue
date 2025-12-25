<template>
  <div class="preference-setup-page">
    <div class="preference-container">
      <h1>취향 설정</h1>
      <p class="subtitle">관심 있는 장르와 분위기를 선택해주세요</p>

      <!-- 관심 장르 섹션 -->
      <section class="preference-section">
        <h2>관심 장르</h2>
        <p class="section-description">좋아하는 장르를 복수 선택해주세요</p>
        <div class="genre-grid">
          <button
            v-for="genre in allGenres"
            :key="genre.id"
            @click="toggleGenre(genre.id)"
            :class="['genre-btn', { active: selectedGenres.includes(genre.id) }]"
          >
            {{ genre.genre_name }}
          </button>
        </div>
      </section>

      <!-- 관심 분위기 섹션 -->
      <section class="preference-section">
        <h2>관심 분위기 / 감정</h2>
        <p class="section-description">선호하는 분위기를 복수 선택해주세요</p>
        <div class="mood-grid">
          <button
            v-for="mood in availableMoods"
            :key="mood"
            @click="toggleMood(mood)"
            :class="['mood-btn', { active: selectedMoods.includes(mood) }]"
          >
            {{ mood }}
          </button>
        </div>
      </section>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="button-group">
        <button @click="skipSetup" class="btn-skip">건너뛰기</button>
        <button @click="savePreferences" class="btn-save" :disabled="isLoading">
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

const allGenres = ref([])
const availableMoods = ref([
  '힐링되는', '웃긴', '감동적인', '우울할 때 보는',
  '긴장감 있는', '생각할 거리 있는', '가볍게 보기 좋은'
])

const selectedGenres = ref([])
const selectedMoods = ref([])
const error = ref('')
const isLoading = ref(false)

// 장르 토글
const toggleGenre = (genreId) => {
  const index = selectedGenres.value.indexOf(genreId)
  if (index > -1) {
    selectedGenres.value.splice(index, 1)
  } else {
    selectedGenres.value.push(genreId)
  }
}

// 분위기 토글
const toggleMood = (mood) => {
  const index = selectedMoods.value.indexOf(mood)
  if (index > -1) {
    selectedMoods.value.splice(index, 1)
  } else {
    selectedMoods.value.push(mood)
  }
}

// 취향 설정 저장
const savePreferences = async () => {
  error.value = ''
  isLoading.value = true

  try {
    await axios.post(
      `${API_URL}/accounts/preferences/`,
      {
        genre_ids: selectedGenres.value,
        moods: selectedMoods.value
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
    error.value = err.response?.data?.detail || '취향 설정 저장에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}

// 건너뛰기
const skipSetup = () => {
  router.push('/')
}

// 장르 목록 가져오기
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
    
    allGenres.value = response.data.all_genres || []
    availableMoods.value = response.data.available_moods || availableMoods.value
    
    // 이미 설정된 취향이 있으면 불러오기
    if (response.data.preferred_genres) {
      selectedGenres.value = response.data.preferred_genres.map(g => g.id)
    }
    if (response.data.preferred_moods) {
      selectedMoods.value = response.data.preferred_moods
    }
  } catch (err) {
    console.error('취향 정보 가져오기 실패:', err)
    // 인증 오류인 경우 로그인 페이지로 리다이렉트
    if (err.response?.status === 401) {
      router.push('/login')
      return
    }
    // 장르 목록은 빈 배열로 시작 (사용자가 직접 선택 가능)
    allGenres.value = []
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
  max-width: 900px;
  background: transparent;
  padding: 60px 40px;
  border: 1px solid #222;
}

h1 {
  font-family: var(--font-display);
  text-align: center;
  margin-bottom: 10px;
  color: var(--text-primary);
  font-size: 3rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -2px;
  line-height: 0.9;
}

.subtitle {
  text-align: center;
  margin-bottom: 50px;
  color: #aaa;
  font-size: 1rem;
  font-family: var(--font-kr);
}

.preference-section {
  margin-bottom: 60px;
}

.preference-section h2 {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: -1px;
}

.section-description {
  margin-bottom: 30px;
  color: #666;
  font-size: 0.9rem;
  font-family: var(--font-kr);
}

.genre-grid,
.mood-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.genre-btn,
.mood-btn {
  padding: 15px 20px;
  background: transparent;
  border: 1px solid #333;
  color: var(--text-primary);
  font-family: var(--font-kr);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  border-radius: 0;
}

.genre-btn:hover,
.mood-btn:hover {
  border-color: var(--accent-acid);
  color: var(--accent-acid);
  transform: translateY(-2px);
}

.genre-btn.active,
.mood-btn.active {
  background: var(--accent-acid);
  border-color: var(--accent-acid);
  color: #000;
  font-weight: 600;
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
  margin-top: 40px;
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
}

/* 반응형 */
@media (max-width: 768px) {
  .preference-container {
    padding: 40px 20px;
  }

  h1 {
    font-size: 2rem;
  }

  .genre-grid,
  .mood-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
  }

  .genre-btn,
  .mood-btn {
    padding: 12px 15px;
    font-size: 0.85rem;
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

