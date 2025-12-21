import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

// Axios 기본 설정
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

export const useMovieStore = defineStore('movie', () => {
  const currentMovie = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // 영화 상세 정보 가져오기
  const getMovieDetail = async (movieId) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`${API_URL}/movies/${movieId}/`)
      currentMovie.value = response.data
      // 리뷰에 showContent 속성 추가 (스포일러 토글용)
      if (currentMovie.value.reviews) {
        currentMovie.value.reviews = currentMovie.value.reviews.map(review => ({
          ...review,
          showContent: false
        }))
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '영화 정보를 불러오는데 실패했습니다.'
      console.error(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 리뷰 작성
  const createReview = async (reviewData) => {
    try {
      const response = await axios.post(`${API_URL}/reviews/`, reviewData)
      // 리뷰 작성 후 영화 정보 다시 불러오기
      await getMovieDetail(reviewData.movie)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '리뷰 작성에 실패했습니다.'
      throw err
    }
  }

  // 리뷰 수정
  const updateReview = async (reviewId, reviewData, movieId) => {
    try {
      const response = await axios.patch(`${API_URL}/reviews/${reviewId}/`, reviewData)
      await getMovieDetail(movieId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '리뷰 수정에 실패했습니다.'
      throw err
    }
  }

  // 리뷰 삭제
  const deleteReview = async (reviewId, movieId) => {
    try {
      await axios.delete(`${API_URL}/reviews/${reviewId}/`)
      await getMovieDetail(movieId)
    } catch (err) {
      error.value = err.response?.data?.detail || '리뷰 삭제에 실패했습니다.'
      throw err
    }
  }

  return {
    currentMovie,
    isLoading,
    error,
    getMovieDetail,
    createReview,
    updateReview,
    deleteReview
  }
})