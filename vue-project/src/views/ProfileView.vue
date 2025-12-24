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
      <!-- 프로필 ID 배지 -->
      <div class="profile-id-section">
        <div class="id-badge hover-trigger">{{ (userProfile?.username || 'USER_01').toUpperCase() }}</div>
        <div class="level-text">LEVEL {{ Math.min(userProfile?.review_count || 0, 10) }} OBSERVER</div>
        
        <!-- 프로필 이미지 (작게) -->
        <div v-if="isOwnProfile" class="profile-image-mini">
          <div class="profile-image-placeholder-mini">
            <img 
              v-if="previewImage || userProfile?.profile_image" 
              :src="previewImage || userProfile?.profile_image" 
              alt="Profile"
              class="profile-image-mini-img"
            />
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleImageSelect"
            style="display: none"
          />
          <button 
            @click="triggerFileInput"
            class="btn-upload-mini"
            :disabled="isUploading"
          >
            {{ isUploading ? 'UPLOADING...' : 'UPLOAD_IMAGE' }}
          </button>
          <div v-if="previewImage" class="upload-actions-mini">
            <button @click="uploadImage" class="btn-save-mini" :disabled="isUploading">SAVE</button>
            <button @click="cancelImageUpload" class="btn-cancel-mini" :disabled="isUploading">CANCEL</button>
          </div>
        </div>
        
        <!-- 팔로우 버튼 (본인이 아닐 때만) -->
        <div v-if="!userProfile?.is_self && userProfile?.id !== authStore.user?.id" class="follow-button-profile">
          <button 
            v-if="!userProfile?.is_following"
            @click="handleFollow"
            class="btn-follow-profile"
            :disabled="isFollowing"
          >
            {{ isFollowing ? 'PROCESSING...' : 'FOLLOW' }}
          </button>
          <button 
            v-else
            @click="handleUnfollow"
            class="btn-unfollow-profile"
            :disabled="isFollowing"
          >
            {{ isFollowing ? 'PROCESSING...' : 'UNFOLLOW' }}
          </button>
        </div>
      </div>

      <!-- 통계 -->
      <div class="profile-stats-modern">
        <div class="stat-item-modern clickable" @click="showFollowersModalHandler">
          <div class="stat-label-modern">FOLLOWERS</div>
          <div class="stat-value-modern">{{ userProfile?.followers_count || 0 }}</div>
        </div>
        <div class="stat-item-modern clickable" @click="showFollowingModalHandler">
          <div class="stat-label-modern">FOLLOWING</div>
          <div class="stat-value-modern">{{ userProfile?.following_count || 0 }}</div>
        </div>
        <div class="stat-item-modern">
          <div class="stat-label-modern">REVIEWS</div>
          <div class="stat-value-modern">{{ userProfile?.review_count || 0 }}</div>
        </div>
      </div>

      <div class="content-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'reviews' }"
          @click="activeTab = 'reviews'"
        >
          REVIEWS
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'wishlist' }"
          @click="activeTab = 'wishlist'"
        >
          WISHLIST
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'report' }"
          @click="activeTab = 'report'"
        >
          REPORT
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

        <!-- 위시리스트 탭 (보고싶은 영화) -->
        <div v-if="activeTab === 'wishlist'" class="watchlist-section">
          <div v-if="wishlistItems.length === 0" class="empty-state">
            위시리스트에 추가한 영화가 없습니다.
          </div>
          <div v-else class="watchlist-grid">
            <div 
              v-for="item in wishlistItems" 
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
          <!-- 히트맵 그리드 -->
          <div class="profile-heatmap-wrapper">
            <div class="heatmap-grid" ref="heatmapRef"></div>
          </div>
          
          <div class="analysis-text">
            ANALYSIS COMPLETE.<br>
            DOMINANT TRAIT: <span class="trait-highlight">VISUAL_SEEKER</span>
          </div>
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
            <div class="report-main-content">
              <div class="report-left">
                <ul class="report-list">
                  <li v-if="preferenceReport.genre_distribution">
                    <strong>TOP 장르</strong>
                    <div class="report-tags">
                      <span v-for="(percent, genre) in preferenceReport.genre_distribution" :key="genre" class="report-tag">
                        {{ genre }} <span class="tag-value">({{ percent }}%)</span>
                      </span>
                    </div>
                  </li>
                  <li v-if="preferenceReport.mood_analysis && preferenceReport.mood_analysis['평균 평점']">
                    <strong>평균 별점</strong>
                    <div class="report-value">{{ preferenceReport.mood_analysis['평균 평점'] }}점</div>
                  </li>
                  <li v-if="preferenceReport.director_preferences">
                    <strong>선호 감독</strong>
                    <div class="report-tags">
                      <span v-for="(count, director) in preferenceReport.director_preferences" :key="director" class="report-tag">
                        {{ director }} <span class="tag-value">({{ count }}편)</span>
                      </span>
                    </div>
                  </li>
                  <li v-if="preferenceReport.top_rated_movies && preferenceReport.top_rated_movies.length > 0">
                    <strong>높은 평점 영화</strong>
                    <div class="report-tags">
                      <span v-for="movie in preferenceReport.top_rated_movies" :key="movie" class="report-tag">
                        {{ movie }}
                      </span>
                    </div>
                  </li>
                </ul>
              </div>
              <div class="report-right">
                <div class="report-visualization">
                  <div v-if="chartData.length === 0" class="chart-empty">
                    <p>차트 데이터가 없습니다.</p>
                    <p class="chart-empty-note">리뷰한 영화에 heaviness와 satisfaction 정보가 필요합니다.</p>
                  </div>
                  <div v-else class="quadrant-chart-container" ref="chartContainer">
                    <svg :width="chartSize" :height="chartSize" class="quadrant-chart">
                      <defs>
                        <!-- 배경 그라데이션 -->
                        <linearGradient id="chartBg" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" style="stop-color:rgba(0,0,0,0.5);stop-opacity:1" />
                          <stop offset="100%" style="stop-color:rgba(20,20,30,0.7);stop-opacity:1" />
                        </linearGradient>
                        
                        <!-- 격자 패턴 -->
                        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(100,100,120,0.2)" stroke-width="0.5"/>
                        </pattern>
                        
                        <!-- 네온 점 효과 (기본) -->
                        <filter id="neon-point" x="-150%" y="-150%" width="400%" height="400%">
                          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                          <feOffset in="coloredBlur" dx="0" dy="0" result="offsetBlur"/>
                          <feFlood flood-color="#6ab7ff" flood-opacity="1"/>
                          <feComposite in2="offsetBlur" operator="in"/>
                          <feMerge>
                            <feMergeNode/>
                            <feMergeNode in="SourceGraphic"/>
                          </feMerge>
                        </filter>
                        
                        <!-- 네온 점 효과 (호버 - 더 강하게) -->
                        <filter id="neon-point-hover" x="-150%" y="-150%" width="400%" height="400%">
                          <feGaussianBlur stdDeviation="6" result="coloredBlur1"/>
                          <feGaussianBlur stdDeviation="3" result="coloredBlur2"/>
                          <feOffset in="coloredBlur1" dx="0" dy="0" result="offsetBlur1"/>
                          <feOffset in="coloredBlur2" dx="0" dy="0" result="offsetBlur2"/>
                          <feFlood flood-color="#8cc8ff" flood-opacity="1"/>
                          <feComposite in2="offsetBlur1" operator="in" result="glow1"/>
                          <feFlood flood-color="#6ab7ff" flood-opacity="1"/>
                          <feComposite in2="offsetBlur2" operator="in" result="glow2"/>
                          <feMerge>
                            <feMergeNode in="glow1"/>
                            <feMergeNode in="glow2"/>
                            <feMergeNode in="SourceGraphic"/>
                          </feMerge>
                        </filter>
                        
                        <!-- 평균 점 네온 효과 (빨간색) -->
                        <filter id="glow-red" x="-150%" y="-150%" width="400%" height="400%">
                          <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
                          <feOffset in="coloredBlur" dx="0" dy="0" result="offsetBlur"/>
                          <feFlood flood-color="#ff3232" flood-opacity="1"/>
                          <feComposite in2="offsetBlur" operator="in"/>
                          <feMerge>
                            <feMergeNode/>
                            <feMergeNode in="SourceGraphic"/>
                          </feMerge>
                        </filter>
                        
                      </defs>
                      
                      <!-- 배경 -->
                      <rect width="100%" height="100%" fill="url(#chartBg)" rx="4"/>
                      <rect width="100%" height="100%" fill="url(#grid)" rx="4"/>
                      
                      <!-- 4사분면 배경 (평균 점 위치에 따라 조건부 색상) -->
                      <rect 
                        :x="chartSize/2" 
                        y="0" 
                        :width="chartSize/2" 
                        :height="chartSize/2" 
                        :fill="quadrantColors.q1" 
                        rx="2"
                        class="quadrant-bg"
                      />
                      <rect 
                        x="0" 
                        y="0" 
                        :width="chartSize/2" 
                        :height="chartSize/2" 
                        :fill="quadrantColors.q2" 
                        rx="2"
                        class="quadrant-bg"
                      />
                      <rect 
                        x="0" 
                        :y="chartSize/2" 
                        :width="chartSize/2" 
                        :height="chartSize/2" 
                        :fill="quadrantColors.q3" 
                        rx="2"
                        class="quadrant-bg"
                      />
                      <rect 
                        :x="chartSize/2" 
                        :y="chartSize/2" 
                        :width="chartSize/2" 
                        :height="chartSize/2" 
                        :fill="quadrantColors.q4" 
                        rx="2"
                        class="quadrant-bg"
                      />
                      
                      <!-- 중심선 -->
                      <line :x1="chartSize/2" y1="0" :x2="chartSize/2" :y2="chartSize" stroke="rgba(204,255,0,0.4)" stroke-width="2" stroke-dasharray="5,5"/>
                      <line x1="0" :y1="chartSize/2" :x2="chartSize" :y2="chartSize/2" stroke="rgba(204,255,0,0.4)" stroke-width="2" stroke-dasharray="5,5"/>
                      
                      <!-- 축 레이블 -->
                      <text :x="chartSize/2" y="18" text-anchor="middle" fill="#ccc" font-size="13" font-weight="600" font-family="var(--font-tech)">대중성</text>
                      <text x="15" :y="chartSize/2" text-anchor="start" fill="#ccc" font-size="13" font-weight="600" font-family="var(--font-tech)" transform="rotate(-90, 15, 200)">무게감</text>
                      
                      <!-- 축 눈금 및 숫자 -->
                      <g class="axis-labels">
                        <text :x="10" :y="chartSize/2 + 4" fill="#888" font-size="11" font-family="var(--font-tech)">0</text>
                        <text :x="chartSize - 10" :y="chartSize/2 + 4" fill="#888" font-size="11" text-anchor="end" font-family="var(--font-tech)">100</text>
                        <text :x="chartSize/2 + 5" :y="18" fill="#888" font-size="11" font-family="var(--font-tech)">100</text>
                        <text :x="chartSize/2 + 5" :y="chartSize - 5" fill="#888" font-size="11" font-family="var(--font-tech)">0</text>
                      </g>
                      
                      <!-- 4사분면 라벨 (모서리에 배치) -->
                      <g class="quadrant-labels">
                        <text x="20" y="30" text-anchor="start" fill="rgba(100,150,255,0.8)" font-size="13" font-weight="700" font-family="var(--font-display)">팝콘 무비</text>
                        <text :x="chartSize - 20" y="30" text-anchor="end" fill="rgba(204,255,0,0.9)" font-size="13" font-weight="700" font-family="var(--font-display)">마스터피스</text>
                        <text x="20" :y="chartSize - 20" text-anchor="start" fill="rgba(150,100,255,0.8)" font-size="13" font-weight="700" font-family="var(--font-display)">매니악</text>
                        <text :x="chartSize - 20" :y="chartSize - 20" text-anchor="end" fill="rgba(255,150,100,0.8)" font-size="13" font-weight="700" font-family="var(--font-display)">시네필</text>
                      </g>
                      
                      <!-- 영화 점들 -->
                      <circle
                        v-for="(review, index) in chartData"
                        :key="review.id || index"
                        :cx="getX(review.satisfaction)"
                        :cy="getY(review.heaviness)"
                        r="5"
                        fill="#6ab7ff"
                        stroke="none"
                        filter="url(#neon-point)"
                        @mouseenter="showTooltip($event, review)"
                        @mouseleave="hideTooltip"
                        class="movie-point"
                      />
                      
                      <!-- 평균 점 (빨간색, 더 눈에 띄게) -->
                      <g v-if="averagePoint">
                        <circle
                          :cx="getX(averagePoint.satisfaction)"
                          :cy="getY(averagePoint.heaviness)"
                          r="10"
                          fill="rgba(255,50,50,0.3)"
                          class="average-point-glow"
                        />
                        <circle
                          :cx="getX(averagePoint.satisfaction)"
                          :cy="getY(averagePoint.heaviness)"
                          r="8"
                          fill="#ff3232"
                          stroke="none"
                          filter="url(#glow-red)"
                          class="average-point"
                        />
                        <text
                          :x="getX(averagePoint.satisfaction)"
                          :y="getY(averagePoint.heaviness) - 15"
                          text-anchor="middle"
                          fill="#ff3232"
                          font-size="11"
                          font-weight="700"
                          font-family="var(--font-tech)"
                        >
                          
                        </text>
                      </g>
                    </svg>
                    
                    <!-- 툴팁 -->
                    <div v-if="tooltip.show" class="chart-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
                      <img v-if="tooltip.data?.movie_poster" :src="tooltip.data.movie_poster" alt="Poster" class="tooltip-poster"/>
                      <div class="tooltip-content">
                        <div class="tooltip-title">{{ tooltip.data?.movie_title }}</div>
                        <div class="tooltip-rating">⭐ {{ tooltip.data?.rating }}점</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="preferenceReport.summary" class="report-summary-wrapper">
              <ul class="report-list">
                <li class="report-summary">
                  <strong>한 줄 요약</strong>
                  <div class="report-summary-text">{{ preferenceReport.summary }}</div>
                </li>
              </ul>
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
import { ref, onMounted, computed, nextTick } from 'vue'
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

// 프로필 이미지 업로드 관련
const fileInput = ref(null)
const previewImage = ref(null)
const selectedFile = ref(null)
const isUploading = ref(false)
const heatmapRef = ref(null)
const chartContainer = ref(null)

// 차트 설정
const chartSize = 400
const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  data: null
})

// 본인 프로필인지 확인하는 computed
const isOwnProfile = computed(() => {
  if (!authStore.isAuthenticated || !userProfile.value || !authStore.user?.id) {
    return false
  }
  return userProfile.value.is_self || userProfile.value.id === authStore.user.id
})

// 위시리스트 (보고싶은 영화 - want 상태)
const wishlistItems = computed(() => {
  return watchlist.value.filter(item => item.status === 'want')
})

// 프로필 정보 가져오기
const fetchProfile = async () => {
  try {
    // URL 쿼리 파라미터에서 user_id 가져오기
    const route = router.currentRoute.value
    const userId = route.query.user
    
    // user_id가 없고 로그인하지 않은 경우 로그인 페이지로 리다이렉트
    if (!userId && !authStore.isAuthenticated) {
      alert('로그인이 필요합니다.')
      router.push('/login')
      return
    }
    
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
    
    // 인증 오류인 경우 로그인 페이지로 리다이렉트
    if (error.response?.status === 401 || error.response?.status === 403) {
      alert('로그인이 필요합니다.')
      router.push('/login')
    }
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
    console.log('[리뷰] 가져온 리뷰 수:', reviews.value.length)
    if (reviews.value.length > 0) {
      console.log('[리뷰] 첫 번째 리뷰 전체 데이터:', reviews.value[0])
      console.log('[리뷰] 첫 번째 리뷰 샘플:', {
        movie_title: reviews.value[0].movie_title,
        movie_heaviness: reviews.value[0].movie_heaviness,
        movie_satisfaction: reviews.value[0].movie_satisfaction,
        'has movie_heaviness': 'movie_heaviness' in reviews.value[0],
        'has movie_satisfaction': 'movie_satisfaction' in reviews.value[0]
      })
    }
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

// 차트 데이터 (heaviness, satisfaction가 있는 리뷰만)
const chartData = computed(() => {
  if (!reviews.value || reviews.value.length === 0) {
    console.log('[차트] 리뷰 데이터가 없습니다')
    return []
  }
  
  console.log('[차트] 전체 리뷰 수:', reviews.value.length)
  console.log('[차트] 첫 번째 리뷰 키들:', reviews.value.length > 0 ? Object.keys(reviews.value[0]) : '없음')
  
  const filtered = reviews.value.filter(review => {
    // movie_heaviness와 movie_satisfaction 필드 확인
    const heaviness = review.movie_heaviness
    const satisfaction = review.movie_satisfaction
    
    const hasHeaviness = heaviness !== null && heaviness !== undefined && heaviness !== ''
    const hasSatisfaction = satisfaction !== null && satisfaction !== undefined && satisfaction !== ''
    
    if (!hasHeaviness || !hasSatisfaction) {
      console.log('[차트] 필터링 제외:', {
        title: review.movie_title,
        heaviness: heaviness,
        satisfaction: satisfaction
      })
    }
    
    return hasHeaviness && hasSatisfaction
  })
  
  console.log('[차트] 필터링된 리뷰 수:', filtered.length)
  if (filtered.length > 0) {
    console.log('[차트] 첫 번째 필터링된 리뷰:', {
      title: filtered[0].movie_title,
      heaviness: filtered[0].movie_heaviness,
      satisfaction: filtered[0].movie_satisfaction
    })
  } else {
    console.log('[차트] 필터링된 리뷰가 없습니다. 모든 리뷰의 필드 값:')
    reviews.value.slice(0, 3).forEach((review, idx) => {
      console.log(`  [${idx}] ${review.movie_title}: heaviness=${review.movie_heaviness}, satisfaction=${review.movie_satisfaction}`)
    })
  }
  
  return filtered.map(review => ({
    id: review.id,
    movie_title: review.movie_title,
    movie_poster: review.movie_poster,
    rating: review.rating,
    heaviness: Number(review.movie_heaviness),
    satisfaction: Number(review.movie_satisfaction)
  }))
})

// 평균 점 계산
const averagePoint = computed(() => {
  if (!chartData.value || chartData.value.length === 0) {
    return null
  }
  const sum = chartData.value.reduce((acc, review) => ({
    heaviness: acc.heaviness + review.heaviness,
    satisfaction: acc.satisfaction + review.satisfaction
  }), { heaviness: 0, satisfaction: 0 })
  
  return {
    heaviness: Math.round(sum.heaviness / chartData.value.length),
    satisfaction: Math.round(sum.satisfaction / chartData.value.length)
  }
})

// 각 사분면의 배경색 계산 (평균 점이 있는 사분면만 라임색 반투명 적용)
const quadrantColors = computed(() => {
  const limeColor = 'rgba(204, 255, 0, 0.2)' // 라임색 반투명
  const transparent = 'transparent'
  
  if (!averagePoint.value) {
    return {
      q1: transparent, // 오른쪽 위 (마스터피스)
      q2: transparent, // 왼쪽 위 (팝콘 무비)
      q3: transparent, // 왼쪽 아래 (매니악)
      q4: transparent // 오른쪽 아래 (시네필)
    }
  }
  
  const satisfaction = averagePoint.value.satisfaction // 0-100, 오른쪽이 높음
  const heaviness = averagePoint.value.heaviness // 0-100, 위가 높음 (getY에서 뒤집어짐)
  
  // 사분면 판단 (satisfaction: x축, heaviness: y축)
  // Q1: 오른쪽 위 (마스터피스) - satisfaction >= 50, heaviness >= 50
  // Q2: 왼쪽 위 (팝콘 무비) - satisfaction < 50, heaviness >= 50
  // Q3: 왼쪽 아래 (매니악) - satisfaction < 50, heaviness < 50
  // Q4: 오른쪽 아래 (시네필) - satisfaction >= 50, heaviness < 50
  
  const isQ1 = satisfaction >= 50 && heaviness >= 50 // 오른쪽 위 (마스터피스)
  const isQ2 = satisfaction < 50 && heaviness >= 50 // 왼쪽 위 (팝콘 무비)
  const isQ3 = satisfaction < 50 && heaviness < 50 // 왼쪽 아래 (매니악)
  const isQ4 = satisfaction >= 50 && heaviness < 50 // 오른쪽 아래 (시네필)
  
  // 평균 점이 있는 사분면만 라임색 반투명 적용
  return {
    q1: isQ1 ? limeColor : transparent,
    q2: isQ2 ? limeColor : transparent,
    q3: isQ3 ? limeColor : transparent,
    q4: isQ4 ? limeColor : transparent
  }
})

// X 좌표 변환 (satisfaction: 0-100 -> x: 0-chartSize)
const getX = (satisfaction) => {
  if (satisfaction === null || satisfaction === undefined) return 0
  return (satisfaction / 100) * chartSize
}

// Y 좌표 변환 (heaviness: 0-100 -> y: chartSize-0, 뒤집어서 위가 100이 되도록)
const getY = (heaviness) => {
  if (heaviness === null || heaviness === undefined) return 0
  return chartSize - (heaviness / 100) * chartSize
}

// 툴팁 표시
const showTooltip = (event, review) => {
  if (!chartContainer.value) return
  
  const rect = chartContainer.value.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // 툴팁을 마우스 오른쪽/아래에 배치하되, 경계를 벗어나지 않도록
  let tooltipX = mouseX + 15
  let tooltipY = mouseY - 10
  
  // 오른쪽 경계 체크
  if (tooltipX + 220 > rect.width) {
    tooltipX = mouseX - 230 // 왼쪽에 배치
  }
  
  // 아래 경계 체크
  if (tooltipY + 110 > rect.height) {
    tooltipY = mouseY - 100 // 위에 배치
  }
  
  tooltip.value = {
    show: true,
    x: tooltipX,
    y: tooltipY,
    data: review
  }
}

// 툴팁 숨기기
const hideTooltip = () => {
  tooltip.value.show = false
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
  // 토큰이 있지만 사용자 정보가 없으면 가져오기
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }
  await fetchProfile()
  await fetchReviews()
  await fetchWatchlist()
  await fetchPreferenceReport()
  
  // 히트맵 그리드 생성
  await nextTick()
  if (heatmapRef.value) {
    for (let i = 0; i < 100; i++) {
      const div = document.createElement('div')
      const randomClass = `c-${Math.floor(Math.random() * 3) + 1}`
      const activeClass = Math.random() > 0.7 ? 'c-active' : ''
      div.className = `heatmap-cell ${randomClass} ${activeClass}`
      heatmapRef.value.appendChild(div)
    }
  }
})

// 프로필 이미지 업로드 관련 함수들
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 파일 크기 체크 (5MB 제한)
    if (file.size > 5 * 1024 * 1024) {
      alert('이미지 크기는 5MB 이하여야 합니다.')
      return
    }
    
    // 파일 타입 체크
    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드할 수 있습니다.')
      return
    }
    
    selectedFile.value = file
    
    // 미리보기 생성
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const uploadImage = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('profile_image', selectedFile.value)
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Token ${authStore.token}`
      }
    }
    
    const url = `${API_URL}/accounts/profile/`
    const response = await axios.patch(url, formData, config)
    
    // 프로필 정보 업데이트
    userProfile.value = response.data
    
    // 미리보기 및 선택된 파일 초기화
    previewImage.value = null
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    // authStore의 사용자 정보도 업데이트
    if (authStore.user) {
      authStore.user.profile_image = response.data.profile_image
    }
    
    // 프로필 정보 다시 가져오기 (이미지 URL 업데이트)
    await fetchProfile()
    
    alert('프로필 이미지가 업로드되었습니다.')
  } catch (error) {
    console.error('이미지 업로드 실패:', error)
    alert('이미지 업로드에 실패했습니다. 다시 시도해주세요.')
  } finally {
    isUploading.value = false
  }
}

const cancelImageUpload = () => {
  previewImage.value = null
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: var(--bg-color);
  color: var(--text-primary);
  min-height: 100vh;
}

.profile-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  z-index: 100;
  mix-blend-mode: difference;
  border-bottom: 1px solid #222;
  margin-bottom: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: -2px;
  font-size: 1.5rem;
  cursor: none;
  color: var(--text-primary);
  width: auto;
  height: auto;
  border-radius: 0;
  background: transparent;
}

.id-badge {
  font-family: var(--font-display);
  font-size: 5rem;
  text-align: center;
  -webkit-text-stroke: 1px #333;
  color: transparent;
  position: relative;
  z-index: 2;
  transition: 0.3s;
  font-weight: 700;
  line-height: 0.9;
}

.id-badge:hover {
  color: var(--text-primary);
}

.level-text {
  font-family: monospace;
  color: #666;
  margin-top: 10px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.btn-nav {
  padding: 10px 20px;
  border-radius: 0;
  border: 1px solid var(--text-primary);
  background: transparent;
  color: var(--text-primary);
  cursor: none;
  font-size: 0.9rem;
  font-family: var(--font-tech);
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s;
}

.btn-nav:hover {
  background: var(--accent-acid);
  color: var(--bg-color);
  border-color: var(--accent-acid);
}

.btn-logout {
  border-color: var(--accent-acid);
  color: var(--accent-acid);
}

.btn-logout:hover {
  background: var(--accent-acid);
  color: var(--bg-color);
}

.profile-content {
  margin-top: 100px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 100px);
}

.profile-id-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 50px;
}

.profile-image-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.profile-image-placeholder-mini {
  width: 80px;
  height: 80px;
  background: #111;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid #333;
  position: relative;
}

.profile-image-mini-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-upload-mini,
.btn-save-mini,
.btn-cancel-mini {
  padding: 8px 16px;
  border-radius: 0;
  border: 1px solid var(--accent-acid);
  background: transparent;
  color: var(--accent-acid);
  cursor: none;
  font-size: 0.7rem;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-upload-mini:hover:not(:disabled),
.btn-save-mini:hover:not(:disabled) {
  background: var(--accent-acid);
  color: var(--bg-color);
}

.btn-cancel-mini {
  border-color: #666;
  color: #666;
}

.btn-cancel-mini:hover:not(:disabled) {
  background: #666;
  color: var(--text-primary);
}

.upload-actions-mini {
  display: flex;
  gap: 10px;
}

.follow-button-profile {
  margin-top: 20px;
}

.btn-follow-profile,
.btn-unfollow-profile {
  padding: 12px 24px;
  border-radius: 0;
  border: 1px solid var(--accent-acid);
  background: transparent;
  color: var(--accent-acid);
  font-size: 0.9rem;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: none;
  transition: all 0.3s;
}

.btn-follow-profile:hover:not(:disabled),
.btn-unfollow-profile:hover:not(:disabled) {
  background: var(--accent-acid);
  color: var(--bg-color);
}

.btn-follow-profile:disabled,
.btn-unfollow-profile:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.profile-stats-modern {
  display: flex;
  gap: 60px;
  align-items: center;
  margin-bottom: 50px;
  padding: 30px 0;
  border-top: 1px solid #222;
  border-bottom: 1px solid #222;
}

.stat-item-modern {
  text-align: center;
  transition: all 0.3s;
}

.stat-item-modern.clickable {
  cursor: none;
}

.stat-item-modern.clickable:hover {
  transform: translateY(-5px);
}

.stat-item-modern.clickable:hover .stat-value-modern {
  color: var(--accent-acid);
}

.stat-label-modern {
  font-family: var(--font-display);
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.stat-value-modern {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  transition: color 0.3s;
}

.content-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 40px;
  border-bottom: 1px solid #222;
}

.tab-btn {
  padding: 15px 30px;
  border-radius: 0;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #666;
  cursor: none;
  font-size: 0.9rem;
  font-family: var(--font-display);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 2px;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: var(--text-primary);
  border-bottom-color: #333;
}

.tab-btn.active {
  color: var(--accent-acid);
  border-bottom-color: var(--accent-acid);
}

.content-area {
  min-height: 400px;
  background: transparent;
  border-radius: 0;
  padding: 0;
  width: 100%;
  max-width: 1000px;
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
  background: transparent;
  border-radius: 0;
  overflow: hidden;
  cursor: none;
  transition: all 0.5s;
  position: relative;
  border: 1px solid #333;
}

.watchlist-card:hover {
  transform: scale(1.05) skewX(-2deg);
  border-color: var(--accent-acid);
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
  background: rgba(204, 255, 0, 0.2);
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  width: 32px;
  height: 32px;
  cursor: none;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  color: var(--accent-acid);
}

.btn-remove-watchlist:hover {
  background: var(--accent-acid);
  color: var(--bg-color);
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
  color: var(--accent-acid);
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
  background: #111;
  padding: 20px;
  border-radius: 0;
  border-left: 3px solid var(--accent-acid);
  cursor: none;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.review-card:hover {
  background: #1a1a1a;
  border-left-color: var(--accent-acid);
  transform: translateX(5px);
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
  color: var(--accent-acid);
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
  background: transparent;
  color: var(--accent-acid);
  border: 1px solid var(--accent-acid);
  padding: 2px 8px;
  border-radius: 0;
  font-size: 11px;
  font-family: var(--font-display);
  text-transform: uppercase;
}

/* Report Section */
.report-section {
  width: 100%;
  padding: 40px 0;
}

.report-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-primary);
}

.report-empty p {
  color: #ffffff;
  font-size: 20px;
  margin-bottom: 25px;
  font-weight: 500;
}

.btn-generate {
  margin-top: 20px;
  padding: 15px 30px;
  background: transparent;
  color: var(--accent-acid);
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 2px;
  transition: all 0.3s;
}

.btn-generate:hover {
  background: var(--accent-acid);
  color: var(--bg-color);
  transform: translateY(-2px);
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 30px;
}

.report-main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.report-header-section {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 25px;
  border-bottom: 2px solid #666;
}

.report-header-section h3 {
  margin: 0 0 8px 0;
  color: #ffffff;
  font-size: 2.5rem;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 3px;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.report-date {
  margin: 0;
  font-size: 15px;
  color: #ddd;
  font-family: var(--font-tech);
  font-weight: 500;
}

.btn-regenerate {
  padding: 12px 24px;
  background: transparent;
  color: var(--accent-acid);
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-regenerate:hover:not(:disabled) {
  background: var(--accent-acid);
  color: var(--bg-color);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(204, 255, 0, 0.3);
}

.btn-regenerate:disabled {
  background: transparent;
  color: #666;
  border-color: #666;
  cursor: not-allowed;
  transform: none;
  opacity: 0.5;
}

.report-left {
  display: flex;
  flex-direction: column;
}

.report-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.report-list li {
  margin-bottom: 25px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.12);
  border: 2px solid #666;
  border-left: 5px solid var(--accent-acid);
  border-radius: 0;
  line-height: 2;
  transition: all 0.3s;
}

.report-list li:hover {
  background: rgba(255, 255, 255, 0.18);
  border-left-color: var(--accent-acid);
  border-color: #777;
  box-shadow: -5px 0 20px rgba(204, 255, 0, 0.4);
}

.report-list li strong {
  display: block;
  margin-bottom: 20px;
  color: var(--accent-acid);
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 1.2rem;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(204, 255, 0, 0.5);
}

.report-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.report-tag {
  display: inline-block;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid #777;
  border-radius: 0;
  font-size: 15px;
  color: #ffffff;
  font-family: var(--font-tech);
  transition: all 0.3s;
  font-weight: 600;
}

.report-tag:hover {
  border-color: var(--accent-acid);
  color: var(--accent-acid);
  background: rgba(204, 255, 0, 0.15);
  box-shadow: 0 0 15px rgba(204, 255, 0, 0.4);
  transform: translateY(-2px);
}

.tag-value {
  color: #ddd;
  font-size: 13px;
  margin-left: 8px;
  font-weight: 500;
}

.report-value {
  margin-top: 20px;
  font-size: 2.5rem;
  color: var(--accent-acid);
  font-family: var(--font-display);
  font-weight: 700;
  text-shadow: 0 0 15px rgba(204, 255, 0, 0.7);
  letter-spacing: 2px;
}

.report-summary-wrapper {
  margin-top: 20px;
}

.report-summary-text {
  margin-top: 20px;
  padding: 25px;
  background: rgba(204, 255, 0, 0.12);
  border: 2px solid rgba(204, 255, 0, 0.5);
  color: #ffffff;
  line-height: 2.2;
  font-family: var(--font-tech);
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 0 20px rgba(204, 255, 0, 0.2);
}

.report-right {
  background: rgba(255, 255, 255, 0.12);
  border: 2px solid #666;
  border-radius: 0;
  padding: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.report-visualization {
  text-align: center;
  color: #ddd;
  font-family: var(--font-tech);
  width: 100%;
}

.report-visualization p {
  margin: 10px 0;
  font-size: 18px;
  font-weight: 500;
}

.visualization-note {
  font-size: 14px;
  margin-top: 15px;
  color: #aaa;
  font-style: italic;
}

/* 4사분면 차트 스타일 */
.quadrant-chart-container {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.quadrant-chart {
  border: 2px solid rgba(204,255,0,0.3);
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 30px rgba(204,255,0,0.1);
  transition: all 0.3s ease;
}

.quadrant-chart:hover {
  border-color: rgba(204,255,0,0.5);
  box-shadow: 0 4px 25px rgba(0,0,0,0.6), 0 0 40px rgba(204,255,0,0.2);
}

.movie-point {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: url(#neon-point);
  fill: #6ab7ff;
}

.movie-point:hover {
  r: 7;
  fill: #8cc8ff;
  filter: url(#neon-point-hover);
  transform-origin: center;
  animation: neon-pulse 1.5s ease-in-out infinite;
}

@keyframes neon-pulse {
  0%, 100% {
    fill: #8cc8ff;
    filter: url(#neon-point-hover);
  }
  50% {
    fill: #a0d4ff;
    filter: url(#neon-point-hover);
  }
}

.average-point {
  cursor: default;
  animation: pulse 2s ease-in-out infinite;
}

.average-point-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    r: 8;
    opacity: 1;
  }
  50% {
    r: 9;
    opacity: 0.9;
  }
}

@keyframes pulse-glow {
  0%, 100% {
    r: 10;
    opacity: 0.3;
  }
  50% {
    r: 12;
    opacity: 0.5;
  }
}

.axis-labels text {
  transition: fill 0.2s;
}

.axis-labels:hover text {
  fill: var(--accent-acid);
}

.quadrant-labels text {
  text-shadow: 0 0 10px rgba(204,255,0,0.5);
  transition: all 0.3s;
}

.quadrant-labels text:hover {
  font-size: 14px;
  filter: brightness(1.2);
}

.quadrant-bg {
  transition: fill 0.5s ease-in-out;
}

.chart-tooltip {
  position: absolute;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(20, 20, 30, 0.98) 100%);
  border: 2px solid var(--accent-acid);
  padding: 15px;
  border-radius: 8px;
  z-index: 1000;
  pointer-events: none;
  min-width: 200px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(204,255,0,0.3);
  display: flex;
  gap: 12px;
  align-items: center;
  backdrop-filter: blur(10px);
  animation: tooltipFadeIn 0.2s ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip-poster {
  width: 60px;
  height: 90px;
  object-fit: cover;
  border-radius: 4px;
  border: 2px solid rgba(204,255,0,0.5);
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
  transition: transform 0.2s;
}

.tooltip-content {
  flex: 1;
}

.tooltip-title {
  color: #fff;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 8px;
  font-family: var(--font-tech);
  text-shadow: 0 0 5px rgba(0,0,0,0.8);
}

.tooltip-rating {
  color: var(--accent-acid);
  font-size: 16px;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(204,255,0,0.5);
}

.chart-empty {
  text-align: center;
  padding: 60px 20px;
  color: #aaa;
}

.chart-empty p {
  margin: 10px 0;
  font-size: 16px;
}

.chart-empty-note {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.chart-empty {
  text-align: center;
  padding: 60px 20px;
  color: #aaa;
}

.chart-empty p {
  margin: 10px 0;
  font-size: 16px;
}

.chart-empty-note {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.analysis-text {
  text-align: center;
  padding: 50px 20px;
  margin: 50px 0;
  font-family: var(--font-display);
  font-size: 1.6rem;
  text-transform: uppercase;
  letter-spacing: 5px;
  color: #ffffff;
  border-top: 2px solid #666;
  border-bottom: 2px solid #666;
  line-height: 2;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.trait-highlight {
  color: var(--accent-acid);
  font-weight: 700;
  text-shadow: 0 0 20px rgba(204, 255, 0, 0.8);
  font-size: 1.8rem;
  letter-spacing: 3px;
}

/* 히트맵 그리드 */
.profile-heatmap-wrapper {
  margin-bottom: 40px;
  display: flex;
  justify-content: center;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 5px;
  opacity: 0.8;
  max-width: 400px;
}

.heatmap-cell {
  width: 30px;
  height: 30px;
  background: #111;
  transition: 0.2s;
  cursor: none;
}

.heatmap-cell:hover {
  background: var(--accent-acid);
  transform: scale(1.5);
  box-shadow: 0 0 10px var(--accent-acid);
}

.heatmap-cell.c-1 {
  background: #222;
}

.heatmap-cell.c-2 {
  background: #333;
}

.heatmap-cell.c-3 {
  background: #444;
}

.heatmap-cell.c-active {
  background: var(--accent-acid);
  opacity: 0.5;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  text-transform: uppercase;
  border-radius: 50%;
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
