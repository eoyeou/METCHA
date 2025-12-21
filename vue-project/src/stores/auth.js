import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const useAuthStore = defineStore('auth', () => {

  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  // Axios 기본 헤더 설정
  const setAuthHeader = () => {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }

  setAuthHeader()

 
  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API_URL}/accounts/login/`, credentials)
      
      token.value = response.data.key
      localStorage.setItem('token', response.data.key)
      
      // 토큰 설정 후 사용자 정보 가져오기
      setAuthHeader()
      await fetchUser()
      
      return { success: true }
    } catch (error) {
      console.error('로그인 실패:', error)
      return { 
        success: false, 
        error: error.response?.data || '로그인에 실패했습니다.' 
      }
    }
  }

  const signup = async (userData) => {
    try {
      const response = await axios.post(`${API_URL}/accounts/signup/`, userData)
      
      token.value = response.data.token
      user.value = response.data.user
      
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      setAuthHeader()
      
      return { success: true }
    } catch (error) {
      console.error('회원가입 실패:', error)
      return { 
        success: false, 
        error: error.response?.data || '회원가입에 실패했습니다.' 
      }
    }
  }

  const logout = async () => {
    try {
      await axios.post(`${API_URL}/accounts/logout/`)
    } catch (error) {
      console.error('로그아웃 요청 실패:', error)
    } finally {
      // 로컬 데이터 삭제
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      setAuthHeader()
    }
  }

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/accounts/profile/`)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('사용자 정보 가져오기 실패:', error)
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUser
  }
})
