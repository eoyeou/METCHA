<template>
  <div class="login-page">
    <div class="login-container">
      <h2>로그인</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="loginForm.username"
            type="text"
            required
            placeholder="아이디를 입력하세요"
          />
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            required
            placeholder="비밀번호를 입력하세요"
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="btn-login" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
        <div class="signup-link">
          계정이 없으신가요? 
          <router-link to="/register">회원가입</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref({
  username: '',
  password: ''
})

const error = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/accounts/login/', loginForm.value)
    
    // 토큰 저장
    const token = response.data.token
    localStorage.setItem('token', token)
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    
    // Auth store 업데이트
    authStore.token = token
    authStore.user = response.data.user
    
    // 홈으로 이동
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.username?.[0] || 
                  err.response?.data?.password?.[0] || 
                  err.response?.data?.detail || 
                  '로그인에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  padding: 20px;
}

.login-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #4a90e2;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background: #fee;
  border-radius: 6px;
}

.btn-login {
  padding: 14px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-login:hover:not(:disabled) {
  background: #357abd;
}

.btn-login:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.signup-link {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.signup-link a {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>
