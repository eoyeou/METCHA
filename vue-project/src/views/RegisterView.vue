<template>
  <div class="register-page">
    <div class="register-container">
      <h2>회원가입</h2>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="registerForm.username"
            type="text"
            required
            minlength="3"
            placeholder="아이디를 입력하세요 (최소 3자)"
          />
        </div>
        <div class="form-group">
          <label for="email">이메일</label>
          <input
            id="email"
            v-model="registerForm.email"
            type="email"
            required
            placeholder="이메일을 입력하세요"
          />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="first_name">이름</label>
            <input
              id="first_name"
              v-model="registerForm.first_name"
              type="text"
              placeholder="이름"
            />
          </div>
          <div class="form-group">
            <label for="last_name">성</label>
            <input
              id="last_name"
              v-model="registerForm.last_name"
              type="text"
              placeholder="성"
            />
          </div>
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            required
            minlength="8"
            placeholder="비밀번호를 입력하세요 (최소 8자)"
          />
        </div>
        <div class="form-group">
          <label for="password_confirm">비밀번호 확인</label>
          <input
            id="password_confirm"
            v-model="registerForm.password_confirm"
            type="password"
            required
            minlength="8"
            placeholder="비밀번호를 다시 입력하세요"
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="btn-register" :disabled="isLoading">
          {{ isLoading ? '가입 중...' : '회원가입' }}
        </button>
        <div class="login-link">
          이미 계정이 있으신가요? 
          <router-link to="/login">로그인</router-link>
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

const registerForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: ''
})

const error = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  error.value = ''
  
  // 비밀번호 확인
  if (registerForm.value.password !== registerForm.value.password_confirm) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  
  isLoading.value = true

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/accounts/register/', registerForm.value)
    
    // 토큰 저장
    const token = response.data.token
    localStorage.setItem('token', token)
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    
    // Auth store 업데이트
    authStore.token = token
    authStore.user = response.data.user
    
    // 홈으로 이동
    alert('회원가입이 완료되었습니다!')
    router.push('/')
  } catch (err) {
    // 에러 메시지 처리
    if (err.response?.data) {
      const errors = err.response.data
      if (errors.username) {
        error.value = `아이디: ${errors.username[0]}`
      } else if (errors.email) {
        error.value = `이메일: ${errors.email[0]}`
      } else if (errors.password) {
        error.value = `비밀번호: ${errors.password[0]}`
      } else if (errors.non_field_errors) {
        error.value = errors.non_field_errors[0]
      } else {
        error.value = '회원가입에 실패했습니다.'
      }
    } else {
      error.value = '회원가입에 실패했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color);
  color: var(--text-primary);
  padding: 20px;
}

.register-container {
  background: transparent;
  padding: 60px 40px;
  border: none;
  border-radius: 0;
  width: 100%;
  max-width: 600px;
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.btn-register {
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

.btn-register:hover:not(:disabled) {
  background: var(--accent-acid);
  color: var(--bg-color);
}

.btn-register:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #888;
  font-size: 0.9rem;
  font-family: var(--font-tech);
}

.login-link a {
  color: var(--accent-acid);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.login-link a:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

