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

        <!-- 오른쪽: 리뷰 작성 버튼 -->
        <div class="review-action">
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
            <div class="review-user">
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
            <button class="btn-like">
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

const route = useRoute()
const router = useRouter()
const movieStore = useMovieStore()
const authStore = useAuthStore()

const movie = computed(() => movieStore.currentMovie)
const showReviewForm = ref(false)
const editingReview = ref(null)

const newReview = ref({
  rating: 0,
  content: '',
  is_spoiler: false
})

// 영화 정보 로드
const loadMovie = async () => {
  const movieId = route.params.id
  try {
    await movieStore.getMovieDetail(movieId)
  } catch (error) {
    console.error('영화 정보 로드 실패:', error)
  }
}

onMounted(() => {
  loadMovie()
})

// 별점 표시
const getStars = (rating) => {
  const fullStars = Math.floor(rating)
  const halfStar = rating % 1 >= 0.5 ? 1 : 0
  const emptyStars = 5 - fullStars - halfStar
  
  return '★'.repeat(fullStars) + 
         (halfStar ? '⯨' : '') + 
         '☆'.repeat(emptyStars)
}

// 날짜 포맷
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

// 이미지 에러 처리
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/300x450?text=No+Image'
}

// 리뷰 폼 토글
const toggleReviewForm = () => {
  showReviewForm.value = !showReviewForm.value
  if (!showReviewForm.value) {
    cancelReview()
  }
}

// 리뷰 작성/수정
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
      // 수정
      await movieStore.updateReview(
        editingReview.value.id,
        newReview.value,
        route.params.id
      )
      alert('리뷰가 수정되었습니다!')
    } else {
      // 작성
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

// 리뷰 수정 시작
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

// 리뷰 취소
const cancelReview = () => {
  editingReview.value = null
  newReview.value = {
    rating: 0,
    content: '',
    is_spoiler: false
  }
}

// 리뷰 삭제
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

// 내 리뷰인지 확인
const isMyReview = (review) => {
  return authStore.user?.username === review.user.username
}

// 스포일러 토글
const toggleSpoiler = (review) => {
  review.showContent = !review.showContent
}

// 네비게이션
const goToProfile = () => {
  router.push('/profile')
}

const goToHome = () => {
  router.push('/')
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

/* 로딩 & 에러 */
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

/* 헤더 */
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

/* 메인 컨텐츠 */
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

/* 리뷰 작성 버튼 */
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

/* 리뷰 폼 */
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

/* 리뷰 섹션 */
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

.review-user {
  display: flex;
  align-items: center;
  gap: 15px;
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

/* 애니메이션 */
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

/* 반응형 */
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