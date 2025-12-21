<template>
  <div class="auth-container">
    <div class="auth-box">
      <div class="auth-header">
        <h1 class="logo" @click="goToHome">MOVIE SITE</h1>
        <h2>로그인</h2>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            placeholder="아이디를 입력하세요"
            required
            class="form-input"
          >
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
            class="form-input"
          >
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>계정이 없으신가요?</p>
        <button @click="goToSignup" class="btn-link">회원가입</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username: '',
  password: ''
})

const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true

  const result = await authStore.login(credentials.value)

  isLoading.value = false

  if (result.success) {
    alert('로그인 성공!')
    router.push('/')
  } else {
    if (result.error.non_field_errors) {
      errorMessage.value = result.error.non_field_errors[0]
    } else if (result.error.detail) {
      errorMessage.value = result.error.detail
    } else {
      errorMessage.value = '로그인에 실패했습니다.'
    }
  }
}

const goToHome = () => router.push('/')
const goToSignup = () => router.push('/signup')
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.auth-box {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 450px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 32px;
  font-weight: bold;
  cursor: pointer;
  background: linear-gradient(45deg, #e94560, #f39c12);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
}

.auth-header h2 {
  font-size: 28px;
  color: #fff;
  margin-top: 10px;
}

.auth-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 16px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #e94560;
  background: rgba(255, 255, 255, 0.15);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.error-message {
  padding: 15px;
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid #e74c3c;
  border-radius: 10px;
  color: #ff6b6b;
  margin-bottom: 20px;
  text-align: center;
}

.btn-submit {
  width: 100%;
  padding: 15px 30px;
  background: linear-gradient(135deg, #e94560 0%, #f39c12 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.auth-footer p {
  color: #aaa;
  margin-bottom: 10px;
}

.btn-link {
  background: none;
  border: none;
  color: #e94560;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: color 0.3s;
}

.btn-link:hover {
  color: #f39c12;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .auth-box {
    padding: 30px 20px;
  }

  .logo {
    font-size: 28px;
  }

  .auth-header h2 {
    font-size: 24px;
  }
}
</style>
