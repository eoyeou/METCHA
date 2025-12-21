import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // 로그인 (임시 - 나중에 구현)
  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API_URL}/accounts/login/`, credentials)
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)
      
      // Axios 헤더에 토큰 설정
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
    } catch (err) {
      throw err
    }
  }

  // 로그아웃
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
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
    logout
  }
})