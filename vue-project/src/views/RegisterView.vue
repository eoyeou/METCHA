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
  background: #f5f5f5;
  padding: 20px;
}

.register-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
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

.btn-register {
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

.btn-register:hover:not(:disabled) {
  background: #357abd;
}

.btn-register:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

