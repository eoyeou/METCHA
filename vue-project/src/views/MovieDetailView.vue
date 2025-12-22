<template>
  <div class="movie-detail-container">
    <!-- 로딩 상태 -->
    <div v-if="movieStore.isLoading" class="loading">
      <div class="spinner"></div>
      <p>로딩 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="movieStore.error" class="error">
      <p>{{ movieStore.error }}</p>
      <button @click="loadMovie" class="btn-retry">다시 시도</button>
    </div>

    <!-- 영화 상세 정보 -->
    <div v-else-if="movie" class="movie-detail">
      <!-- 헤더 -->
      <header class="movie-header">
        <div class="logo" @click="$router.push('/')">MOVIE SITE</div>
        <div class="header-buttons">
          <button @click="goToProfile" class="btn-header">내 프로필</button>
          <button @click="goToHome" class="btn-header">홈으로</button>
        </div>
      </header>

      <!-- 메인 컨텐츠 -->
      <div class="movie-content">
        <!-- 왼쪽: 포스터 -->
        <div class="movie-poster">
          <img 
            :src="movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Image'" 
            :alt="movie.title"
            @error="handleImageError"
          >
        </div>

        <!-- 중앙: 영화 정보 -->
        <div class="movie-info">
          <h1 class="movie-title">{{ movie.title }}</h1>
          <p class="original-title" v-if="movie.original_title">
            {{ movie.original_title }}
          </p>
          
          <div class="rating-info">
            <span class="stars">{{ getStars(movie.avg_rating) }}</span>
            <span class="rating-number">{{ movie.avg_rating.toFixed(1) }}</span>
            <span class="review-count">({{ movie.review_count }}개의 리뷰)</span>
          </div>

          <div class="movie-meta">
            <div class="meta-item">
              <span class="meta-label">개봉년도</span>
              <span class="meta-value">{{ movie.release_year }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">상영시간</span>
              <span class="meta-value">{{ movie.runtime }}분</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">감독</span>
              <span class="meta-value">{{ movie.director }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">출연</span>
              <span class="meta-value">{{ movie.cast }}</span>
            </div>
          </div>

          <div class="genre-tags">
            <span 
              v-for="genre in movie.genres" 
              :key="genre.id" 
              class="genre-tag"
            >
              {{ genre.genre_name }}
            </span>
          </div>

          <div class="movie-description">
            <h3>줄거리</h3>
            <p>{{ movie.description || '줄거리 정보가 없습니다.' }}</p>
          </div>
        </div>

        <!-- 오른쪽: 리뷰 작성 버튼 및 위시리스트 버튼 -->
        <div class="review-action">
          <!-- 위시리스트 버튼 (하트) -->
          <button 
            v-if="authStore.isAuthenticated"
            @click="toggleWatchlist" 
            class="btn-watchlist"
            :class="{ active: isInWatchlist }"
            :disabled="isTogglingWatchlist"
          >
            <span class="heart-icon">{{ isInWatchlist ? '❤️' : '🤍' }}</span>
            <span>{{ isInWatchlist ? '위시리스트에서 제거' : '위시리스트에 추가' }}</span>
          </button>
          <button 
            v-else
            @click="$router.push('/login')" 
            class="btn-watchlist"
          >
            <span class="heart-icon">🤍</span>
            <span>위시리스트에 추가</span>
          </button>
          
          <button 
            v-if="authStore.isAuthenticated"
            @click="toggleReviewForm" 
            class="btn-write-review"
            :class="{ active: showReviewForm }"
          >
            {{ showReviewForm ? '작성 취소' : '이 영화 리뷰 작성하기' }}
          </button>
          <button 
            v-else
            @click="$router.push('/login')" 
            class="btn-write-review"
          >
            로그인 후 리뷰 작성
          </button>
        </div>
      </div>

      <!-- 리뷰 작성 폼 -->
      <transition name="slide-down">
        <div v-if="showReviewForm" class="review-form">
          <h3>{{ editingReview ? '리뷰 수정' : '리뷰 작성' }}</h3>
          <form @submit.prevent="submitReview">
            <div class="form-group">
              <label>평점 *</label>
              <div class="rating-input">
                <button
                  v-for="n in 5"
                  :key="n"
                  type="button"
                  @click="newReview.rating = n"
                  class="star-btn"
                  :class="{ active: newReview.rating >= n }"
                >
                  {{ newReview.rating >= n ? '★' : '☆' }}
                </button>
                <span class="rating-text">{{ newReview.rating || 0 }}점</span>
              </div>
            </div>

            <div class="form-group">
              <label>리뷰 내용 *</label>
              <textarea 
                v-model="newReview.content" 
                rows="6" 
                placeholder="영화에 대한 솔직한 리뷰를 작성해주세요"
                required
              ></textarea>
              <div class="char-count">
                {{ newReview.content.length }} / 500자
              </div>
            </div>

            <div class="form-group checkbox-group">
              <label>
                <input type="checkbox" v-model="newReview.is_spoiler">
                <span>스포일러 포함</span>
              </label>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-submit">
                {{ editingReview ? '수정 완료' : '작성 완료' }}
              </button>
              <button type="button" @click="cancelReview" class="btn-cancel">
                취소
              </button>
            </div>
          </form>
        </div>
      </transition>

      <!-- 리뷰 목록 -->
      <div class="reviews-section">
        <h2>리뷰 {{ movie.reviews.length }}개</h2>
        
        <div v-if="movie.reviews.length === 0" class="no-reviews">
          <p>아직 작성된 리뷰가 없습니다.</p>
          <p>첫 번째 리뷰를 작성해보세요!</p>
        </div>

        <div 
          v-for="review in movie.reviews" 
          :key="review.id" 
          class="review-card"
        >
          <div class="review-header">
            <div class="review-user-section">
              <div 
                class="review-user clickable"
                @click="goToUserProfile(review.user.id)"
              >
                <img 
                  :src="review.user.profile_image || 'https://via.placeholder.com/40'" 
                  alt="프로필"
                  class="user-avatar"
                >
                <div class="user-info">
                  <span class="username">{{ review.user.username }}</span>
                  <span class="review-date">{{ formatDate(review.created_at) }}</span>
                </div>
              </div>
              <!-- 팔로우 버튼 (본인이 아니고 로그인한 경우만) -->
              <button 
                v-if="shouldShowFollowButton(review)"
                @click.stop="toggleFollow(review.user.id, review.user)"
                class="btn-follow-review"
                :class="{ 'following': review.user.is_following }"
              >
                {{ review.user.is_following ? '언팔로우' : '팔로우' }}
              </button>
            </div>
            <div class="review-rating">
              <span class="stars">{{ getStars(review.rating) }}</span>
              <span class="rating-number">{{ review.rating }}</span>
            </div>
          </div>
          
          <div class="review-content">
            <p 
              :class="{ 
                spoiler: review.is_spoiler && !review.showContent,
                'spoiler-visible': review.is_spoiler && review.showContent
              }"
            >
              {{ review.content }}
            </p>
            <button 
              v-if="review.is_spoiler" 
              @click="toggleSpoiler(review)"
              class="btn-spoiler"
            >
              {{ review.showContent ? '⚠️ 스포일러 숨기기' : '⚠️ 스포일러 보기' }}
            </button>
          </div>

          <div class="review-actions">
            <button 
              @click="handleLikeReview(review.id)"
              class="btn-like"
              :class="{ 'liked': review.is_liked }"
            >
              <span>👍</span>
              <span>{{ review.likes_count }}</span>
            </button>
            <template v-if="isMyReview(review)">
              <button 
                @click="startEditReview(review)"
                class="btn-edit"
              >
                ✏️ 수정
              </button>
              <button 
                @click="handleDeleteReview(review.id)"
                class="btn-delete"
              >
                🗑️ 삭제
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const movieStore = useMovieStore()
const authStore = useAuthStore()

// Axios 기본 설정
const API_URL = 'http://127.0.0.1:8000/api'
if (authStore.token) {
  axios.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
}

const movie = computed(() => movieStore.currentMovie)
const showReviewForm = ref(false)
const editingReview = ref(null)
const isInWatchlist = ref(false)
const isTogglingWatchlist = ref(false)

const newReview = ref({
  rating: 0,
  content: '',
  is_spoiler: false
})

const loadMovie = async () => {
  const movieId = route.params.id
  try {
    await movieStore.getMovieDetail(movieId)
    // 로그인한 사용자 정보가 없으면 프로필 정보 가져오기
    if (authStore.isAuthenticated && !authStore.user) {
      try {
        const API_URL = 'http://127.0.0.1:8000/api'
        const response = await axios.get(`${API_URL}/accounts/profile/`, {
          headers: {
            'Authorization': `Token ${authStore.token}`
          }
        })
        authStore.user = response.data
      } catch (error) {
        console.error('사용자 정보 로드 실패:', error)
      }
    }
    // 위시리스트 확인
    if (authStore.isAuthenticated) {
      await checkWatchlist(movieId)
    }
  } catch (error) {
    console.error('영화 정보 로드 실패:', error)
  }
}

// 위시리스트 확인
const checkWatchlist = async (movieId) => {
  if (!authStore.isAuthenticated || !authStore.token) {
    isInWatchlist.value = false
    return
  }
  
  try {
    const checkUrl = `${API_URL}/watchlists/${movieId}/check/`
    console.log('위시리스트 확인 URL:', checkUrl)
    
    const response = await axios.get(checkUrl, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })
    console.log('위시리스트 확인 응답:', response.data)
    isInWatchlist.value = response.data.is_in_watchlist
  } catch (error) {
    console.error('위시리스트 확인 실패:', error)
    // 확인 실패 시 기본값으로 false 설정
    isInWatchlist.value = false
  }
}

// 위시리스트 토글
const toggleWatchlist = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  if (!authStore.token) {
    alert('로그인 토큰이 없습니다. 다시 로그인해주세요.')
    router.push('/login')
    return
  }
  
  const movieId = parseInt(route.params.id)
  console.log('=== 위시리스트 토글 시작 ===')
  console.log('영화 ID:', movieId)
  console.log('현재 상태:', isInWatchlist.value ? '위시리스트에 있음' : '위시리스트에 없음')
  console.log('토큰:', authStore.token ? '있음' : '없음')
  
  isTogglingWatchlist.value = true
  
  try {
    if (isInWatchlist.value) {
      // 위시리스트에서 제거
      console.log('위시리스트에서 제거 시도...')
      const deleteUrl = `${API_URL}/watchlists/${movieId}/`
      console.log('DELETE URL:', deleteUrl)
      
      const response = await axios.delete(deleteUrl, {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      })
      console.log('✅ 제거 성공:', response.status)
      isInWatchlist.value = false
      alert('위시리스트에서 제거되었습니다.')
    } else {
      // 위시리스트에 추가
      console.log('위시리스트에 추가 시도...')
      const postUrl = `${API_URL}/watchlists/`
      console.log('POST URL:', postUrl)
      console.log('요청 데이터:', { movie_id: movieId })
      
      const response = await axios.post(postUrl, {
        movie_id: movieId
      }, {
        headers: {
          'Authorization': `Token ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      })
      console.log('✅ 추가 성공:', response.status, response.data)
      isInWatchlist.value = true
      alert('위시리스트에 추가되었습니다!')
    }
    console.log('=== 위시리스트 토글 완료 ===')
  } catch (error) {
    console.error('❌ 위시리스트 토글 실패!')
    console.error('에러 객체:', error)
    console.error('에러 메시지:', error.message)
    console.error('에러 코드:', error.code)
    
    if (error.response) {
      console.error('응답 상태:', error.response.status)
      console.error('응답 데이터:', error.response.data)
      console.error('응답 헤더:', error.response.headers)
      
      const errorMessage = error.response.data?.detail || 
                          error.response.data?.message || 
                          `서버 오류 (${error.response.status})`
      alert(`위시리스트 처리에 실패했습니다.\n\n${errorMessage}`)
    } else if (error.request) {
      console.error('요청은 보냈지만 응답이 없음:', error.request)
      alert('서버에 연결할 수 없습니다. Django 서버가 실행 중인지 확인하세요.')
    } else {
      console.error('요청 설정 중 에러:', error.message)
      alert(`위시리스트 처리에 실패했습니다.\n\n${error.message}`)
    }
    console.error('=== 에러 상세 끝 ===')
  } finally {
    isTogglingWatchlist.value = false
  }
}

onMounted(async () => {
  // 로그인한 사용자 정보가 없으면 가져오기
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      const response = await axios.get(`${API_URL}/accounts/profile/`, {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      })
      authStore.user = response.data
    } catch (error) {
      console.error('사용자 정보 로드 실패:', error)
    }
  }
  await loadMovie()
})

const getStars = (rating) => {
  const fullStars = Math.floor(rating)
  const halfStar = rating % 1 >= 0.5 ? 1 : 0
  const emptyStars = 5 - fullStars - halfStar
  
  return '★'.repeat(fullStars) + 
         (halfStar ? '⯨' : '') + 
         '☆'.repeat(emptyStars)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return `${diffDays}일 전`
  
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/300x450?text=No+Image'
}

const toggleReviewForm = () => {
  showReviewForm.value = !showReviewForm.value
  if (!showReviewForm.value) {
    cancelReview()
  }
}

const submitReview = async () => {
  if (!newReview.value.rating) {
    alert('평점을 선택해주세요.')
    return
  }

  if (!newReview.value.content.trim()) {
    alert('리뷰 내용을 입력해주세요.')
    return
  }

  try {
    if (editingReview.value) {
      await movieStore.updateReview(
        editingReview.value.id,
        newReview.value,
        route.params.id
      )
      alert('리뷰가 수정되었습니다!')
    } else {
      await movieStore.createReview({
        movie: route.params.id,
        ...newReview.value
      })
      alert('리뷰가 작성되었습니다!')
    }
    
    cancelReview()
    showReviewForm.value = false
  } catch (error) {
    alert(error.response?.data?.detail || '리뷰 저장에 실패했습니다.')
  }
}

const startEditReview = (review) => {
  editingReview.value = review
  newReview.value = {
    rating: review.rating,
    content: review.content,
    is_spoiler: review.is_spoiler
  }
  showReviewForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelReview = () => {
  editingReview.value = null
  newReview.value = {
    rating: 0,
    content: '',
    is_spoiler: false
  }
}

const handleDeleteReview = async (reviewId) => {
  if (confirm('정말 삭제하시겠습니까?')) {
    try {
      await movieStore.deleteReview(reviewId, route.params.id)
      alert('리뷰가 삭제되었습니다.')
    } catch (error) {
      alert('리뷰 삭제에 실패했습니다.')
    }
  }
}

const handleLikeReview = async (reviewId) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  
  try {
    await movieStore.toggleReviewLike(reviewId, route.params.id)
  } catch (error) {
    alert('좋아요 처리에 실패했습니다.')
  }
}

const isMyReview = (review) => {
  if (!authStore.user || !review.user) return false
  // ID와 username 둘 다 체크하여 더 정확하게 판단
  return authStore.user.id === review.user.id || authStore.user.username === review.user.username
}

// 팔로우 버튼 표시 여부 결정
const shouldShowFollowButton = (review) => {
  // 로그인하지 않은 경우 표시 안 함
  if (!authStore.isAuthenticated) {
    return false
  }
  
  // 리뷰 작성자 정보가 없는 경우 표시 안 함
  if (!review || !review.user || !review.user.id) {
    return false
  }
  
  // 현재 로그인한 사용자 정보가 없는 경우 표시 안 함 (안전을 위해)
  if (!authStore.user || !authStore.user.id) {
    console.log('사용자 정보 없음 - 팔로우 버튼 숨김')
    return false
  }
  
  // 현재 로그인한 사용자와 리뷰 작성자가 같은 경우 표시 안 함 (가장 먼저 체크)
  if (review.user.id === authStore.user.id) {
    console.log('본인 리뷰 - 팔로우 버튼 숨김', {
      reviewUserId: review.user.id,
      currentUserId: authStore.user.id
    })
    return false
  }
  
  // username으로도 체크 (ID가 없을 경우 대비)
  if (review.user.username && authStore.user.username && review.user.username === authStore.user.username) {
    console.log('본인 리뷰 (username) - 팔로우 버튼 숨김', {
      reviewUsername: review.user.username,
      currentUsername: authStore.user.username
    })
    return false
  }
  
  // 본인 리뷰인 경우 표시 안 함
  if (isMyReview(review)) {
    console.log('isMyReview true - 팔로우 버튼 숨김')
    return false
  }
  
  return true
}

const toggleSpoiler = (review) => {
  review.showContent = !review.showContent
}

const goToProfile = () => {
  router.push('/profile')
}

const goToHome = () => {
  router.push('/')
}

// 사용자 프로필로 이동
const goToUserProfile = (userId) => {
  router.push(`/profile?user=${userId}`)
}

// 팔로우/언팔로우 토글
const toggleFollow = async (userId, user) => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  const isFollowing = user.is_following
  
  try {
    if (isFollowing) {
      const response = await axios.delete(
        `${API_URL}/accounts/users/${userId}/follow/`,
        {
          headers: {
            'Authorization': `Token ${authStore.token}`
          }
        }
      )
      console.log('언팔로우 성공:', response.data)
      user.is_following = false
    } else {
      const response = await axios.post(
        `${API_URL}/accounts/users/${userId}/follow/`,
        {},
        {
          headers: {
            'Authorization': `Token ${authStore.token}`
          }
        }
      )
      console.log('팔로우 성공:', response.data)
      user.is_following = true
    }
    // 영화 정보 새로고침하여 팔로워 수 업데이트
    await loadMovie()
  } catch (error) {
    console.error('팔로우/언팔로우 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert(error.response?.data?.detail || error.response?.data?.message || '처리에 실패했습니다.')
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.movie-detail-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.1);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-retry {
  padding: 10px 30px;
  background: #e94560;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.movie-header {
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

.movie-content {
  display: grid;
  grid-template-columns: 300px 1fr 250px;
  gap: 40px;
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.movie-poster img {
  width: 100%;
  border-radius: 15px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s;
}

.movie-poster img:hover {
  transform: scale(1.05);
}

.movie-info {
  padding: 20px 0;
}

.movie-title {
  font-size: 42px;
  margin-bottom: 10px;
  font-weight: bold;
}

.original-title {
  color: #aaa;
  font-size: 18px;
  margin-bottom: 20px;
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
  font-size: 20px;
}

.stars {
  color: #f39c12;
  font-size: 24px;
}

.rating-number {
  font-weight: bold;
  font-size: 24px;
}

.review-count {
  color: #aaa;
}

.movie-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.meta-label {
  color: #aaa;
  font-size: 14px;
}

.meta-value {
  font-size: 16px;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
}

.genre-tag {
  padding: 8px 16px;
  background: rgba(233, 69, 96, 0.2);
  border: 1px solid #e94560;
  border-radius: 20px;
  font-size: 14px;
}

.movie-description {
  margin-top: 30px;
}

.movie-description h3 {
  font-size: 24px;
  margin-bottom: 15px;
}

.movie-description p {
  line-height: 1.8;
  color: #ddd;
  font-size: 16px;
}

.btn-watchlist {
  width: 100%;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.btn-watchlist:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-watchlist.active {
  background: rgba(233, 69, 96, 0.3);
  border-color: #e94560;
}

.btn-watchlist:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.heart-icon {
  font-size: 24px;
}

.btn-write-review {
  width: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #e94560 0%, #f39c12 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
}

.btn-write-review:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(233, 69, 96, 0.6);
}

.btn-write-review.active {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
}

.review-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 15px;
  margin: 0 40px 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.review-form h3 {
  font-size: 24px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 16px;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 36px;
  cursor: pointer;
  color: #555;
  transition: all 0.2s;
}

.star-btn.active {
  color: #f39c12;
  transform: scale(1.2);
}

.star-btn:hover {
  transform: scale(1.3);
}

.rating-text {
  font-size: 18px;
  font-weight: bold;
  margin-left: 10px;
}

.form-group textarea {
  width: 100%;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 16px;
  resize: vertical;
  font-family: inherit;
}

.form-group textarea:focus {
  outline: none;
  border-color: #e94560;
}

.char-count {
  text-align: right;
  color: #aaa;
  font-size: 14px;
  margin-top: 5px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-submit, .btn-cancel {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-submit {
  background: #e94560;
  color: white;
  flex: 1;
}

.btn-submit:hover {
  background: #d63851;
  transform: translateY(-2px);
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.reviews-section {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.reviews-section h2 {
  font-size: 32px;
  margin-bottom: 30px;
}

.no-reviews {
  text-align: center;
  padding: 60px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
}

.no-reviews p {
  margin: 10px 0;
  color: #aaa;
  font-size: 18px;
}

.review-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 30px;
  margin-bottom: 20px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.review-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.review-user-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.review-user.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.review-user.clickable:hover {
  opacity: 0.8;
}

.review-user.clickable:hover .username {
  color: #e94560;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid #e94560;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.username {
  font-weight: bold;
  font-size: 16px;
  transition: color 0.3s;
}

.review-date {
  color: #aaa;
  font-size: 14px;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
}

.review-rating .stars {
  color: #f39c12;
}

.review-content {
  margin: 20px 0;
}

.review-content p {
  line-height: 1.8;
  font-size: 16px;
  color: #ddd;
}

.spoiler {
  filter: blur(8px);
  user-select: none;
  cursor: not-allowed;
  transition: filter 0.3s;
}

.spoiler-visible {
  filter: none;
  user-select: auto;
  cursor: auto;
}

.btn-follow-review {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #4a90e2;
  background: #4a90e2;
  color: white;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-follow-review:hover {
  background: #357abd;
  border-color: #357abd;
}

.btn-follow-review.following {
  background: transparent;
  color: #4a90e2;
  border-color: #4a90e2;
}

.btn-follow-review.following:hover {
  background: #e74c3c;
  border-color: #e74c3c;
  color: white;
}

.btn-spoiler {
  margin-top: 15px;
  padding: 8px 16px;
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid #ffc107;
  color: #ffc107;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-spoiler:hover {
  background: rgba(255, 193, 7, 0.3);
}

.review-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-like, .btn-edit, .btn-delete {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-like:hover {
  background: rgba(52, 152, 219, 0.3);
  border-color: #3498db;
}

.btn-edit:hover {
  background: rgba(243, 156, 18, 0.3);
  border-color: #f39c12;
}

.btn-delete {
  color: #e74c3c;
  border-color: #e74c3c;
}

.btn-delete:hover {
  background: rgba(231, 76, 60, 0.3);
}

.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@media (max-width: 1024px) {
  .movie-content {
    grid-template-columns: 250px 1fr;
    gap: 30px;
  }
  
  .review-action {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .movie-content {
    grid-template-columns: 1fr;
    padding: 20px;
  }
  
  .movie-header {
    padding: 15px 20px;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .movie-title {
    font-size: 28px;
  }
  
  .reviews-section {
    padding: 20px;
  }
}
</style>
