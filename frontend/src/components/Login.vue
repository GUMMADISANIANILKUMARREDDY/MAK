<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/api'

const router = useRouter()
const emit = defineEmits(['close', 'switch-to-register'])

const form = ref({
  identifier: '',
  password: '',
})

const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const step = ref('login') // 'login' | 'forgot' | 'reset'
const forgotEmail = ref('')
const resetForm = ref({ email: '', otp: '', newPassword: '', confirmPassword: '' })

const handleLogin = async () => {
  error.value = ''
  successMsg.value = ''
  loading.value = true
  try {
    const identifierRaw = (form.value.identifier || '').trim()
    const password = (form.value.password || '').trim()
    const payload = identifierRaw.includes('@')
      ? { email: identifierRaw.toLowerCase(), password }
      : { userid: identifierRaw, password }
    const response = await authService.login(payload)
    const ok = response?.success === true || Boolean(response?.access_token)
    if (ok) {
      localStorage.setItem('access_token', response.access_token)
      if (response.refresh_token) localStorage.setItem('refresh_token', response.refresh_token)
      let userToStore = response.user
      if (!userToStore || typeof userToStore !== 'object') {
        try {
          const me = await authService.getMe()
          if (me && typeof me === 'object') userToStore = me
        } catch (_) {}
      }
      if (userToStore && typeof userToStore === 'object') {
        localStorage.setItem('user', JSON.stringify(userToStore))
      }
      emit('close')
      router.push('/dashboard')
    } else {
      error.value = response.message || 'Login failed'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const openForgot = () => {
  step.value = 'forgot'
  error.value = ''
  successMsg.value = ''
  forgotEmail.value = ''
}

const handleForgotPassword = async () => {
  error.value = ''
  successMsg.value = ''
  loading.value = true
  try {
    const res = await authService.forgotPassword(forgotEmail.value.trim())
    if (res.success) {
      successMsg.value = res.message || 'Reset code sent to your email.'
      resetForm.value.email = forgotEmail.value.trim()
      resetForm.value.otp = ''
      resetForm.value.newPassword = ''
      resetForm.value.confirmPassword = ''
      step.value = 'reset'
    } else {
      error.value = res.message || 'Failed to send reset code'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to send reset code.'
  } finally {
    loading.value = false
  }
}

const handleResetPassword = async () => {
  error.value = ''
  successMsg.value = ''
  if (resetForm.value.newPassword !== resetForm.value.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }
  loading.value = true
  try {
    const res = await authService.resetPassword(
      resetForm.value.email,
      resetForm.value.otp,
      resetForm.value.newPassword
    )
    if (res.success) {
      successMsg.value = 'Password reset. You can log in with your new password.'
      step.value = 'login'
    } else {
      error.value = res.message || 'Reset failed'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Reset failed. Try again.'
  } finally {
    loading.value = false
  }
}

const backToLogin = () => {
  step.value = 'login'
  error.value = ''
  successMsg.value = ''
}
</script>

<template>
  <div class="auth-form auth-login">
    <template v-if="step === 'login'">
      <h2>Welcome Back</h2>
      <p class="auth-sub">Sign in to access your dashboard</p>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>User ID / Email</label>
          <input
            v-model="form.identifier"
            type="text"
            placeholder="Enter user ID or email"
            :disabled="loading"
            required
          />
        </div>

        <div class="field">
          <label>Password</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            :disabled="loading"
            required
          />
        </div>

        <p class="forgot-row">
          <a href="#" @click.prevent="openForgot">Forgot password?</a>
        </p>

        <div v-if="error" class="msg msg-error">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="auth-switch">
        Don't have an account?
        <a href="#" @click.prevent="emit('switch-to-register')">Register here</a>
      </p>
    </template>

    <template v-else-if="step === 'forgot'">
      <h2>Forgot Password</h2>
      <p class="auth-sub">Enter your email to receive a reset code</p>
      <form @submit.prevent="handleForgotPassword">
        <div class="field">
          <label>Email</label>
          <input v-model="forgotEmail" type="email" placeholder="Your registered email" required />
        </div>
        <div v-if="error" class="msg msg-error">{{ error }}</div>
        <div v-if="successMsg" class="msg msg-success">{{ successMsg }}</div>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send reset code' }}
        </button>
        <p class="auth-switch">
          <a href="#" @click.prevent="backToLogin">Back to login</a>
        </p>
      </form>
    </template>

    <template v-else-if="step === 'reset'">
      <h2>Reset Password</h2>
      <p class="auth-sub">Enter the code from your email and a new password</p>
      <form @submit.prevent="handleResetPassword">
        <div class="field">
          <label>Email</label>
          <input v-model="resetForm.email" type="email" disabled />
        </div>
        <div class="field">
          <label>Reset code (OTP)</label>
          <input v-model="resetForm.otp" type="text" placeholder="6-digit code" maxlength="6" required />
        </div>
        <div class="field">
          <label>New password</label>
          <input v-model="resetForm.newPassword" type="password" placeholder="New password" required />
        </div>
        <div class="field">
          <label>Confirm new password</label>
          <input v-model="resetForm.confirmPassword" type="password" placeholder="Confirm" required />
        </div>
        <div v-if="error" class="msg msg-error">{{ error }}</div>
        <div v-if="successMsg" class="msg msg-success">{{ successMsg }}</div>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Resetting...' : 'Reset password' }}
        </button>
        <p class="auth-switch">
          <a href="#" @click.prevent="backToLogin">Back to login</a>
        </p>
      </form>
    </template>
  </div>
</template>

<style scoped>
.auth-form {
  width: 100%;
}

.auth-form h2 {
  font-size: 1.65rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.4rem;
}

.auth-sub {
  font-size: 0.95rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.field {
  margin-bottom: 1.15rem;
}

.field label {
  display: block;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}

.field input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #f8fafc;
  color: #0f172a;
}

.field input:focus {
  outline: none;
  border-color: #2080FF;
  background: white;
  box-shadow: 0 0 0 4px rgba(32, 128, 255, 0.12);
}

.field input::placeholder {
  color: #94a3b8;
}

.forgot-row {
  margin-top: -0.4rem;
  margin-bottom: 1rem;
  text-align: right;
}

.forgot-row a {
  color: #2080FF;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
}

.forgot-row a:hover {
  color: #00BF80;
  text-decoration: underline;
}

.msg {
  padding: 0.7rem 1rem;
  border-radius: 10px;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.msg-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.msg-success {
  background: #f0fdf9;
  border: 1px solid #99f6e4;
  color: #0d9488;
}

.btn-submit {
  width: 100%;
  padding: 0.85rem 1rem;
  background: linear-gradient(135deg, #2080FF 0%, #00BF80 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 8px 24px rgba(32, 128, 255, 0.35);
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  margin-top: 1.25rem;
  font-size: 0.95rem;
  color: #64748b;
}

.auth-switch a {
  color: #2080FF;
  font-weight: 600;
  text-decoration: none;
}

.auth-switch a:hover {
  color: #00BF80;
  text-decoration: underline;
}
</style>
