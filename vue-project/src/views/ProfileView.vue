<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="header-left">
        <div class="logo" @click="goToHome">logo</div>
        <h1 class="username">{{ userProfile?.username || 'USER 1' }}</h1>
      </div>
      <div class="header-right">
        <button 
          v-if="!userProfile?.is_self && authStore.isAuthenticated"
          class="btn-nav" 
          @click="goToMyProfile"
        >
          내 프로필
        </button>
        <button 
          v-else
          class="btn-nav" 
          @click="goToHome"
        >
          홈
        </button>
        <button class="btn-nav" @click="goToReviewCreate">리뷰작성</button>
        <button 
          v-if="authStore.isAuthenticated"
          class="btn-nav btn-logout" 
          @click="handleLogout"
        >
          로그아웃
        </button>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-info">
        <div class="profile-image-placeholder">
          <img 
            v-if="userProfile?.profile_image" 
            :src="userProfile.profile_image" 
            alt="Profile"
            class="profile-image"
          />
          <div v-else class="profile-image-placeholder-text">User Profile Image</div>
        </div>
        
        <div class="profile-stats">
          <div class="stat-item">
            <div class="stat-label">리뷰 수</div>
            <div class="stat-value">{{ userProfile?.review_count || 0 }}</div>
          </div>
          <div class="stat-item clickable" @click="showFollowersModalHandler">
            <div class="stat-label">팔로워</div>
            <div class="stat-value">{{ userProfile?.followers_count || 0 }}</div>
          </div>
          <div class="stat-item clickable" @click="showFollowingModalHandler">
            <div class="stat-label">팔로잉</div>
            <div class="stat-value">{{ userProfile?.following_count || 0 }}</div>
          </div>
        </div>
        
        <!-- 팔로우 버튼 (본인이 아닐 때만 표시) -->
        <div v-if="!userProfile?.is_self && userProfile?.id !== authStore.user?.id" class="follow-button-container">
          <button 
            v-if="!userProfile?.is_following"
            @click="handleFollow"
            class="btn-follow"
            :disabled="isFollowing"
          >
            {{ isFollowing ? '처리 중...' : '팔로우' }}
          </button>
          <button 
            v-else
            @click="handleUnfollow"
            class="btn-unfollow"
            :disabled="isFollowing"
          >
            {{ isFollowing ? '처리 중...' : '언팔로우' }}
          </button>
        </div>
      </div>

      <div class="content-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'reviews' }"
          @click="activeTab = 'reviews'"
        >
          내 Review
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'watchlist' }"
          @click="activeTab = 'watchlist'"
        >
          위시리스트
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'report' }"
          @click="activeTab = 'report'"
        >
          내 취향 Report
        </button>
      </div>

      <div class="content-area">
        <!-- 내 Review 탭 -->
        <div v-if="activeTab === 'reviews'" class="reviews-section">
          <div v-if="reviews.length === 0" class="empty-state">
            작성한 리뷰가 없습니다.
          </div>
          <div v-else class="reviews-list">
            <div 
              v-for="review in reviews" 
              :key="review.id"
              class="review-card"
              @click="goToMovie(review.movie_id)"
            >
              <div class="review-movie-poster">
                <img 
                  v-if="review.movie_poster" 
                  :src="review.movie_poster" 
                  :alt="review.movie_title"
                />
                <div v-else class="poster-placeholder">No Image</div>
              </div>
              <div class="review-content">
                <h3 class="review-movie-title">{{ review.movie_title }}</h3>
                <div class="review-rating">⭐ {{ review.rating.toFixed(1) }}</div>
                <p class="review-text">{{ review.content }}</p>
                <div class="review-meta">
                  <span v-if="review.is_spoiler" class="spoiler-badge">스포일러</span>
                  <span class="review-date">{{ formatDate(review.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 위시리스트 탭 -->
        <div v-if="activeTab === 'watchlist'" class="watchlist-section">
          <div v-if="watchlist.length === 0" class="empty-state">
            위시리스트에 추가한 영화가 없습니다.
          </div>
          <div v-else class="watchlist-grid">
            <div 
              v-for="item in watchlist" 
              :key="item.id"
              class="watchlist-card"
              @click="goToMovie(item.movie.id)"
            >
              <div class="watchlist-poster">
                <img 
                  v-if="item.movie.poster_url" 
                  :src="item.movie.poster_url" 
                  :alt="item.movie.title"
                />
                <div v-else class="poster-placeholder">No Image</div>
                <div class="watchlist-overlay">
                  <button 
                    @click.stop="removeFromWatchlist(item.movie.id)"
                    class="btn-remove-watchlist"
                  >
                    ❌
                  </button>
                </div>
              </div>
              <div class="watchlist-info">
                <h3 class="watchlist-title">{{ item.movie.title }}</h3>
                <p class="watchlist-year">{{ item.movie.release_year }}</p>
                <div class="watchlist-rating">
                  ⭐ {{ item.movie.avg_rating.toFixed(1) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 내 취향 Report 탭 -->
        <div v-if="activeTab === 'report'" class="report-section">
          <div v-if="!preferenceReport" class="report-empty">
            <p>취향 리포트가 없습니다.</p>
            <button class="btn-generate" @click="generateReport">리포트 생성하기</button>
          </div>
          <div v-else class="report-content">
            <div class="report-header-section">
              <div>
                <h3>취향 분석</h3>
                <p v-if="preferenceReport.generated_at" class="report-date">
                  최종 분석일: {{ formatDate(preferenceReport.generated_at) }}
                </p>
              </div>
              <button 
                class="btn-regenerate" 
                @click="regenerateReport"
                :disabled="isGeneratingReport"
              >
                {{ isGeneratingReport ? '분석 중...' : '취향 다시 분석하기' }}
              </button>
            </div>
            <div class="report-left">
              <ul class="report-list">
                <li v-if="preferenceReport.genre_distribution">
                  <strong>TOP 장르:</strong>
                  <span v-for="(percent, genre) in preferenceReport.genre_distribution" :key="genre">
                    {{ genre }} ({{ percent }}%)
                  </span>
                </li>
                <li v-if="preferenceReport.mood_analysis">
                  <strong>평균 별점:</strong> {{ preferenceReport.mood_analysis['평균 평점'] }}점
                </li>
                <li v-if="preferenceReport.director_preferences">
                  <strong>선호 감독:</strong>
                  <span v-for="(count, director) in preferenceReport.director_preferences" :key="director">
                    {{ director }} ({{ count }}편)
                  </span>
                </li>
                <li v-if="preferenceReport.top_rated_movies && preferenceReport.top_rated_movies.length > 0">
                  <strong>높은 평점 영화:</strong>
                  <span v-for="movie in preferenceReport.top_rated_movies" :key="movie">
                    {{ movie }}
                  </span>
                </li>
                <li v-if="preferenceReport.summary">
                  <strong>한 줄 요약:</strong> {{ preferenceReport.summary }}
                </li>
              </ul>
            </div>
            <div class="report-right">
              <div class="report-visualization">
                <p>시각화 영역</p>
                <p class="visualization-note">(네트워크 그래프 등 추후 구현)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 팔로워 목록 모달 -->
    <div v-if="showFollowersModal" class="modal-overlay" @click="showFollowersModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>팔로워</h3>
          <button class="modal-close" @click="showFollowersModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="followers.length === 0" class="empty-list">
            팔로워가 없습니다.
          </div>
          <div v-else class="user-list">
            <div 
              v-for="user in followers" 
              :key="user.id"
              class="user-item"
              @click="goToUserProfile(user.id)"
            >
              <div class="user-avatar">
                <img 
                  v-if="user.profile_image" 
                  :src="user.profile_image" 
                  :alt="user.username"
                />
                <div v-else class="avatar-placeholder">{{ user.username[0] }}</div>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-stats">리뷰 {{ user.review_count }}개</div>
              </div>
              <button 
                v-if="!user.is_following && user.id !== currentUserId"
                @click.stop="toggleFollow(user.id, user)"
                class="btn-follow-small"
              >
                팔로우
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 팔로잉 목록 모달 -->
    <div v-if="showFollowingModal" class="modal-overlay" @click="showFollowingModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>팔로잉</h3>
          <button class="modal-close" @click="showFollowingModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="following.length === 0" class="empty-list">
            팔로잉한 사용자가 없습니다.
          </div>
          <div v-else class="user-list">
            <div 
              v-for="user in following" 
              :key="user.id"
              class="user-item"
              @click="goToUserProfile(user.id)"
            >
              <div class="user-avatar">
                <img 
                  v-if="user.profile_image" 
                  :src="user.profile_image" 
                  :alt="user.username"
                />
                <div v-else class="avatar-placeholder">{{ user.username[0] }}</div>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-stats">리뷰 {{ user.review_count }}개</div>
              </div>
              <button 
                v-if="userProfile?.is_self || user.is_following"
                @click.stop="toggleUnfollow(user.id, user)"
                class="btn-unfollow-small"
              >
                언팔로우
              </button>
            </div>
          </div>
        </div>
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

// Axios 기본 설정
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

// 토큰이 있으면 헤더에 설정
if (authStore.token) {
  axios.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
}

const userProfile = ref(null)
const reviews = ref([])
const watchlist = ref([])
const preferenceReport = ref(null)
const activeTab = ref('reviews')
const isLoading = ref(false)
const isFollowing = ref(false)
const isGeneratingReport = ref(false)
const showFollowersModal = ref(false)
const showFollowingModal = ref(false)
const followers = ref([])
const following = ref([])
const currentUserId = ref(null)

// 프로필 정보 가져오기
const fetchProfile = async () => {
  try {
    // URL 쿼리 파라미터에서 user_id 가져오기
    const route = router.currentRoute.value
    const userId = route.query.user
    
    let url = `${API_URL}/accounts/profile/`
    if (userId) {
      url = `${API_URL}/accounts/profile/${userId}/`
    }
    
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const response = await axios.get(url, config)
    userProfile.value = response.data
    
    // is_self 필드가 없거나 잘못된 경우 프론트엔드에서 직접 계산
    if (authStore.user?.id) {
      userProfile.value.is_self = userProfile.value.id === authStore.user.id
    } else {
      userProfile.value.is_self = false
    }
    
    currentUserId.value = authStore.user?.id || null
    console.log('프로필 로드 완료:', {
      userProfileId: userProfile.value.id,
      currentUserId: currentUserId.value,
      is_self: userProfile.value.is_self
    })
  } catch (error) {
    console.error('프로필 정보 로드 실패:', error)
    console.error('에러 상세:', error.response?.data)
  }
}

// 리뷰 목록 가져오기
const fetchReviews = async () => {
  try {
    const route = router.currentRoute.value
    const userId = route.query.user
    
    let url = `${API_URL}/accounts/profile/reviews/`
    if (userId) {
      url = `${API_URL}/accounts/profile/reviews/${userId}/`
    }
    
    const response = await axios.get(url)
    reviews.value = response.data
  } catch (error) {
    console.error('리뷰 목록 로드 실패:', error)
  }
}

// 위시리스트 가져오기
const fetchWatchlist = async () => {
  try {
    const route = router.currentRoute.value
    const userId = route.query.user
    
    // 본인 위시리스트만 조회 가능
    if (userId && userId !== authStore.user?.id?.toString()) {
      watchlist.value = []
      return
    }
    
    if (!authStore.isAuthenticated) {
      watchlist.value = []
      return
    }
    
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const response = await axios.get(`${API_URL}/watchlists/`, config)
    watchlist.value = response.data
  } catch (error) {
    console.error('위시리스트 로드 실패:', error)
    watchlist.value = []
  }
}

// 위시리스트에서 제거
const removeFromWatchlist = async (movieId) => {
  if (!confirm('위시리스트에서 제거하시겠습니까?')) {
    return
  }
  
  try {
    await axios.delete(`${API_URL}/watchlists/${movieId}/`, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })
    // 위시리스트 다시 가져오기
    await fetchWatchlist()
  } catch (error) {
    console.error('위시리스트 제거 실패:', error)
    alert('위시리스트에서 제거하는데 실패했습니다.')
  }
}

// 취향 리포트 가져오기
const fetchPreferenceReport = async () => {
  try {
    const route = router.currentRoute.value
    const userId = route.query.user
    
    let url = `${API_URL}/accounts/profile/preference-report/`
    if (userId) {
      url = `${API_URL}/accounts/profile/preference-report/${userId}/`
    }
    
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    console.log('리포트 가져오기 URL:', url)
    
    const response = await axios.get(url, config)
    console.log('리포트 가져오기 성공:', response.data)
    preferenceReport.value = response.data
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('취향 리포트 로드 실패:', error)
      console.error('에러 상세:', error.response?.data)
    } else {
      console.log('리포트 없음 (404)')
      preferenceReport.value = null
    }
  }
}

// 리포트 생성
const generateReport = async () => {
  isGeneratingReport.value = true
  try {
    const route = router.currentRoute.value
    const userId = route.query.user
    
    let url = `${API_URL}/accounts/profile/preference-report/`
    if (userId) {
      url = `${API_URL}/accounts/profile/preference-report/${userId}/`
    }
    
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const response = await axios.post(url, {}, config)
    console.log('리포트 생성 성공:', response.data)
    
    // 리포트를 다시 가져와서 최신 데이터로 업데이트
    await fetchPreferenceReport()
    
    alert('취향 리포트가 생성되었습니다!')
  } catch (error) {
    console.error('리포트 생성 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert(error.response?.data?.detail || '리포트 생성에 실패했습니다.')
  } finally {
    isGeneratingReport.value = false
  }
}

// 취향 리포트 다시 분석하기
const regenerateReport = async () => {
  if (!confirm('현재까지 작성된 리뷰를 기반으로 취향 리포트를 다시 분석하시겠습니까?')) {
    return
  }
  
  console.log('=== 취향 리포트 재생성 시작 ===')
  isGeneratingReport.value = true
  
  try {
    const route = router.currentRoute.value
    const userId = route.query.user
    
    let url = `${API_URL}/accounts/profile/preference-report/`
    if (userId) {
      url = `${API_URL}/accounts/profile/preference-report/${userId}/`
    }
    
    console.log('API URL:', url)
    console.log('현재 사용자:', authStore.user)
    console.log('토큰:', authStore.token ? '있음' : '없음')
    
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    console.log('리포트 생성 요청 전송...')
    const response = await axios.post(url, {}, config)
    console.log('리포트 재생성 성공:', response.data)
    console.log('응답 상태:', response.status)
    
    // 리포트를 다시 가져와서 최신 데이터로 업데이트
    console.log('최신 리포트 가져오기...')
    await fetchPreferenceReport()
    console.log('리포트 업데이트 완료:', preferenceReport.value)
    
    alert('취향 리포트가 업데이트되었습니다!')
  } catch (error) {
    console.error('리포트 재생성 실패:', error)
    console.error('에러 상세:', error.response?.data)
    console.error('에러 상태:', error.response?.status)
    console.error('에러 헤더:', error.response?.headers)
    alert(error.response?.data?.detail || error.response?.data?.message || '리포트 재생성에 실패했습니다.')
  } finally {
    isGeneratingReport.value = false
    console.log('=== 취향 리포트 재생성 종료 ===')
  }
}

// 날짜 포맷팅
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR')
}

// 영화 상세 페이지로 이동
const goToMovie = (movieId) => {
  router.push(`/movies/${movieId}`)
}

// 리뷰 작성 페이지로 이동
const goToReviewCreate = () => {
  router.push('/reviews/create')
}

// 홈으로 이동
const goToHome = () => {
  router.push('/')
}

// 내 프로필로 이동
const goToMyProfile = () => {
  router.push('/profile').then(() => {
    // 프로필 정보 새로고침
    fetchProfile()
    fetchReviews()
  })
}

// 로그아웃
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

// 팔로우
const handleFollow = async () => {
  console.log('팔로우 버튼 클릭')
  console.log('userProfile:', userProfile.value)
  console.log('authStore.isAuthenticated:', authStore.isAuthenticated)
  console.log('authStore.token:', authStore.token)
  
  if (!userProfile.value) {
    console.error('userProfile이 없습니다.')
    return
  }
  
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  
  if (!authStore.token) {
    alert('토큰이 없습니다. 다시 로그인해주세요.')
    router.push('/login')
    return
  }
  
  const targetUserId = userProfile.value.id
  console.log('팔로우 대상 ID:', targetUserId)
  console.log('API URL:', `${API_URL}/accounts/users/${targetUserId}/follow/`)
  
  isFollowing.value = true
  try {
    const response = await axios.post(
      `${API_URL}/accounts/users/${targetUserId}/follow/`,
      {},
      {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      }
    )
    console.log('팔로우 성공:', response.data)
    console.log('응답 상태:', response.status)
    
    // 현재 보고 있는 프로필 정보 새로고침 (상대방의 팔로워 수 업데이트)
    // 쿼리 파라미터를 유지하면서 새로고침
    const route = router.currentRoute.value
    const userId = route.query.user
    
    if (userId) {
      // 다른 사용자의 프로필을 보고 있는 경우
      console.log('다른 사용자 프로필 새로고침:', userId)
      const config = {}
      if (authStore.token) {
        config.headers = {
          'Authorization': `Token ${authStore.token}`
        }
      }
      const profileResponse = await axios.get(
        `${API_URL}/accounts/profile/${userId}/`,
        config
      )
      console.log('프로필 새로고침 성공:', profileResponse.data)
      userProfile.value = profileResponse.data
    } else {
      // 내 프로필을 보고 있는 경우
      console.log('내 프로필 새로고침')
      await fetchProfile()
      await Promise.all([
        fetchFollowers(),
        fetchFollowing()
      ])
    }
    console.log('팔로우 후 userProfile:', userProfile.value)
  } catch (error) {
    console.error('팔로우 실패:', error)
    console.error('에러 상세:', error.response?.data)
    console.error('에러 상태:', error.response?.status)
    console.error('에러 헤더:', error.response?.headers)
    alert(error.response?.data?.detail || error.response?.data?.message || '팔로우에 실패했습니다.')
  } finally {
    isFollowing.value = false
  }
}

// 언팔로우
const handleUnfollow = async () => {
  if (!userProfile.value) return
  
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  
  const targetUserId = userProfile.value.id
  
  isFollowing.value = true
  try {
    const response = await axios.delete(
      `${API_URL}/accounts/users/${targetUserId}/follow/`,
      {
        headers: {
          'Authorization': `Token ${authStore.token}`
        }
      }
    )
    console.log('언팔로우 성공:', response.data)
    
    // 현재 보고 있는 프로필 정보 새로고침 (상대방의 팔로워 수 업데이트)
    // 쿼리 파라미터를 유지하면서 새로고침
    const route = router.currentRoute.value
    const userId = route.query.user
    
    if (userId) {
      // 다른 사용자의 프로필을 보고 있는 경우
      const config = {}
      if (authStore.token) {
        config.headers = {
          'Authorization': `Token ${authStore.token}`
        }
      }
      const profileResponse = await axios.get(
        `${API_URL}/accounts/profile/${userId}/`,
        config
      )
      userProfile.value = profileResponse.data
    } else {
      // 내 프로필을 보고 있는 경우
      await fetchProfile()
      await Promise.all([
        fetchFollowers(),
        fetchFollowing()
      ])
    }
  } catch (error) {
    console.error('언팔로우 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert(error.response?.data?.detail || error.response?.data?.message || '언팔로우에 실패했습니다.')
  } finally {
    isFollowing.value = false
  }
}

// 팔로워 목록 가져오기
const fetchFollowers = async () => {
  if (!userProfile.value) return
  
  try {
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const response = await axios.get(
      `${API_URL}/accounts/users/${userProfile.value.id}/followers/`,
      config
    )
    followers.value = response.data
  } catch (error) {
    console.error('팔로워 목록 로드 실패:', error)
    console.error('에러 상세:', error.response?.data)
  }
}

// 팔로잉 목록 가져오기
const fetchFollowing = async () => {
  if (!userProfile.value) {
    console.error('userProfile이 없습니다.')
    return
  }
  
  try {
    const config = {}
    if (authStore.token) {
      config.headers = {
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const userId = userProfile.value.id
    console.log('팔로잉 목록 가져오기:', userId)
    
    const response = await axios.get(
      `${API_URL}/accounts/users/${userId}/following/`,
      config
    )
    console.log('팔로잉 목록 응답:', response.data)
    following.value = response.data
  } catch (error) {
    console.error('팔로잉 목록 로드 실패:', error)
    console.error('에러 상세:', error.response?.data)
    following.value = []
  }
}

// 모달 열 때 목록 가져오기
const openFollowersModal = async () => {
  showFollowersModal.value = true
  await fetchFollowers()
}

const openFollowingModal = async () => {
  console.log('팔로잉 모달 열기')
  showFollowingModal.value = true
  await fetchFollowing()
  console.log('팔로잉 목록:', following.value)
}

// 모달 열기 함수로 변경
const showFollowersModalHandler = () => {
  openFollowersModal()
}

const showFollowingModalHandler = () => {
  openFollowingModal()
}

// 목록에서 팔로우/언팔로우 토글
const toggleFollow = async (userId, user) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  
  try {
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
    
    // 현재 보고 있는 프로필 정보 새로고침
    const route = router.currentRoute.value
    const currentUserId = route.query.user
    
    if (currentUserId) {
      // 다른 사용자의 프로필을 보고 있는 경우
      const config = {}
      if (authStore.token) {
        config.headers = {
          'Authorization': `Token ${authStore.token}`
        }
      }
      const profileResponse = await axios.get(
        `${API_URL}/accounts/profile/${currentUserId}/`,
        config
      )
      userProfile.value = profileResponse.data
    } else {
      // 내 프로필을 보고 있는 경우
      await fetchProfile()
      await Promise.all([
        fetchFollowers(),
        fetchFollowing()
      ])
    }
  } catch (error) {
    console.error('팔로우 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert(error.response?.data?.detail || error.response?.data?.message || '팔로우에 실패했습니다.')
  }
}

const toggleUnfollow = async (userId, user) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }
  
  try {
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
    
    // 현재 보고 있는 프로필 정보 새로고침
    const route = router.currentRoute.value
    const currentUserId = route.query.user
    
    if (currentUserId) {
      // 다른 사용자의 프로필을 보고 있는 경우
      const config = {}
      if (authStore.token) {
        config.headers = {
          'Authorization': `Token ${authStore.token}`
        }
      }
      const profileResponse = await axios.get(
        `${API_URL}/accounts/profile/${currentUserId}/`,
        config
      )
      userProfile.value = profileResponse.data
    } else {
      // 내 프로필을 보고 있는 경우
      await fetchProfile()
      await Promise.all([
        fetchFollowers(),
        fetchFollowing()
      ])
    }
    
    // 팔로잉 목록에서 제거
    following.value = following.value.filter(u => u.id !== userId)
  } catch (error) {
    console.error('언팔로우 실패:', error)
    console.error('에러 상세:', error.response?.data)
    alert(error.response?.data?.detail || error.response?.data?.message || '언팔로우에 실패했습니다.')
  }
}

// 다른 사용자 프로필로 이동
const goToUserProfile = (userId) => {
  router.push(`/profile?user=${userId}`).then(() => {
    fetchProfile()
    fetchReviews()
  })
}

onMounted(async () => {
  await fetchProfile()
  await fetchReviews()
  await fetchWatchlist()
  await fetchPreferenceReport()
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #ddd;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
}

.username {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
}

.header-right {
  display: flex;
  gap: 10px;
}

.btn-nav {
  padding: 10px 20px;
  border-radius: 20px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-nav:hover {
  background: #f5f5f5;
}

.btn-logout {
  background: #e74c3c;
  color: white;
  border-color: #e74c3c;
}

.btn-logout:hover {
  background: #c0392b;
}

.profile-content {
  margin-top: 30px;
}

.profile-info {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.profile-image-placeholder {
  width: 150px;
  height: 150px;
  background: #e0e0e0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.profile-image-placeholder-text {
  color: #999;
  font-size: 12px;
  text-align: center;
}

.profile-stats {
  display: flex;
  gap: 40px;
  align-items: center;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-item.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-item.clickable:hover {
  transform: translateY(-2px);
  color: #4a90e2;
}

.follow-button-container {
  margin-top: 20px;
}

.btn-follow,
.btn-unfollow {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-follow {
  background: #4a90e2;
  color: white;
}

.btn-follow:hover:not(:disabled) {
  background: #357abd;
}

.btn-unfollow {
  background: #95a5a6;
  color: white;
}

.btn-unfollow:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-follow:disabled,
.btn-unfollow:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.content-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 12px 24px;
  border-radius: 20px;
  border: 2px solid #333;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.tab-btn.active {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.content-area {
  min-height: 400px;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 30px;
}

/* Watchlist Section */
.watchlist-section {
  width: 100%;
}

.watchlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.watchlist-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.watchlist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.watchlist-poster {
  width: 100%;
  aspect-ratio: 2/3;
  position: relative;
  overflow: hidden;
}

.watchlist-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.watchlist-overlay {
  position: absolute;
  top: 0;
  right: 0;
  padding: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.watchlist-card:hover .watchlist-overlay {
  opacity: 1;
}

.btn-remove-watchlist {
  background: rgba(231, 76, 60, 0.9);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-remove-watchlist:hover {
  background: rgba(231, 76, 60, 1);
  transform: scale(1.1);
}

.watchlist-info {
  padding: 12px;
}

.watchlist-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.watchlist-year {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: #666;
}

.watchlist-rating {
  font-size: 14px;
  color: #f39c12;
  font-weight: bold;
}

/* Reviews Section */
.reviews-section {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  display: flex;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.review-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.review-movie-poster {
  width: 100px;
  height: 150px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
}

.review-movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #999;
}

.review-content {
  flex: 1;
}

.review-movie-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: bold;
}

.review-rating {
  font-size: 16px;
  margin-bottom: 10px;
  color: #f39c12;
}

.review-text {
  margin: 10px 0;
  color: #555;
  line-height: 1.6;
}

.review-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
  color: #999;
}

.spoiler-badge {
  background: #e74c3c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

/* Report Section */
.report-section {
  width: 100%;
}

.report-empty {
  text-align: center;
  padding: 60px 20px;
}

.btn-generate {
  margin-top: 20px;
  padding: 12px 24px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-generate:hover {
  background: #357abd;
}

.report-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.report-header-section {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.report-header-section h3 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 24px;
}

.report-date {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.btn-regenerate {
  padding: 10px 20px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-regenerate:hover:not(:disabled) {
  background: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

.btn-regenerate:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.report-header-section {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.report-header-section h3 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 24px;
}

.report-date {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.btn-regenerate {
  padding: 10px 20px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-regenerate:hover:not(:disabled) {
  background: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

.btn-regenerate:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.report-left h3 {
  margin-bottom: 20px;
  color: #333;
}

.report-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.report-list li {
  margin-bottom: 15px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  line-height: 1.8;
}

.report-list li strong {
  display: block;
  margin-bottom: 5px;
  color: #333;
}

.report-list li span {
  display: inline-block;
  margin-right: 10px;
  padding: 4px 8px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 13px;
}

.report-right {
  background: white;
  border-radius: 8px;
  padding: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.report-visualization {
  text-align: center;
  color: #999;
}

.visualization-note {
  font-size: 12px;
  margin-top: 10px;
  color: #bbb;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.modal-close:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.empty-list {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.user-item:hover {
  background: #f5f5f5;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: #4a90e2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.user-stats {
  font-size: 14px;
  color: #999;
}

.btn-follow-small,
.btn-unfollow-small {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-follow-small {
  background: #4a90e2;
  color: white;
}

.btn-follow-small:hover {
  background: #357abd;
}

.btn-unfollow-small {
  background: #e0e0e0;
  color: #333;
}

.btn-unfollow-small:hover {
  background: #d0d0d0;
}
</style>
