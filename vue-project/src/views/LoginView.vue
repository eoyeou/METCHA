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
  background: var(--bg-color);
  color: var(--text-primary);
  padding: 20px;
}

.login-container {
  background: transparent;
  padding: 60px 40px;
  border: none;
  border-radius: 0;
  width: 100%;
  max-width: 500px;
  border: 1px solid #222;
}

h2 {
  font-family: var(--font-display);
  text-align: center;
  margin-bottom: 40px;
  color: var(--text-primary);
  font-size: 3rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -2px;
  line-height: 0.9;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

label {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

input {
  padding: 15px 20px;
  background: transparent;
  border: none;
  border-bottom: 2px solid #333;
  border-radius: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-family: var(--font-tech);
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-bottom-color: var(--accent-acid);
  letter-spacing: 1px;
}

input::placeholder {
  color: #333;
  -webkit-text-stroke: 1px #333;
  color: transparent;
}

.error-message {
  color: var(--accent-acid);
  font-size: 0.9rem;
  text-align: center;
  padding: 15px;
  background: rgba(204, 255, 0, 0.1);
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  font-family: var(--font-tech);
}

.btn-login {
  padding: 20px;
  background: transparent;
  color: var(--accent-acid);
  border: 1px solid var(--accent-acid);
  border-radius: 0;
  font-size: 1rem;
  font-weight: 500;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 2px;
  cursor: none;
  transition: all 0.3s;
}

.btn-login:hover:not(:disabled) {
  background: var(--accent-acid);
  color: var(--bg-color);
}

.btn-login:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.signup-link {
  text-align: center;
  margin-top: 20px;
  color: #888;
  font-size: 0.9rem;
  font-family: var(--font-tech);
}

.signup-link a {
  color: var(--accent-acid);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.signup-link a:hover {
  color: var(--text-primary);
  text-decoration: underline;
}
</style>
