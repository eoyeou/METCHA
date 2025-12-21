import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // 로그인
  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API_URL}/accounts/login/`, credentials)
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)
      
      // Axios 헤더에 토큰 설정
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      return response.data
    } catch (err) {
      throw err
    }
  }

  // 회원가입
  const register = async (userData) => {
    try {
      const response = await axios.post(`${API_URL}/accounts/register/`, userData)
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)
      
      // Axios 헤더에 토큰 설정
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      return response.data
    } catch (err) {
      throw err
    }
  }

  // 로그아웃
  const logout = async () => {
    try {
      await axios.post(`${API_URL}/accounts/logout/`)
    } catch (err) {
      console.error('로그아웃 실패:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }

  // 초기화 시 토큰이 있으면 헤더에 설정
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout
  }
})