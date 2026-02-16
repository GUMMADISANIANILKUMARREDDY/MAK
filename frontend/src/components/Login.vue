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

// Forgot / Reset password
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
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
      }
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
  <div class="login-form">
    <!-- Login -->
    <template v-if="step === 'login'">
      <h2>Welcome Back</h2>
      <p class="subtitle">Login to access your dashboard</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>User ID / Email</label>
          <input
            v-model="form.identifier"
            type="text"
            placeholder="Enter your user ID or email"
            :disabled="loading"
            required
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            :disabled="loading"
            required
          />
        </div>

        <p class="forgot-link">
          <a href="#" @click.prevent="openForgot">Forgot password?</a>
        </p>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span>{{ loading ? 'Logging in...' : 'Login' }}</span>
        </button>
      </form>
    </template>

    <!-- Forgot: request OTP -->
    <template v-else-if="step === 'forgot'">
      <h2>Forgot Password</h2>
      <p class="subtitle">Enter your email to receive a reset code</p>
      <form @submit.prevent="handleForgotPassword">
        <div class="form-group">
          <label>Email</label>
          <input v-model="forgotEmail" type="email" placeholder="Your registered email" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMsg" class="success-message">{{ successMsg }}</div>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send reset code' }}
        </button>
        <p class="switch-text">
          <a href="#" @click.prevent="backToLogin">Back to login</a>
        </p>
      </form>
    </template>

    <!-- Reset: OTP + new password -->
    <template v-else-if="step === 'reset'">
      <h2>Reset Password</h2>
      <p class="subtitle">Enter the code from your email and a new password</p>
      <form @submit.prevent="handleResetPassword">
        <div class="form-group">
          <label>Email</label>
          <input v-model="resetForm.email" type="email" disabled />
        </div>
        <div class="form-group">
          <label>Reset code (OTP)</label>
          <input v-model="resetForm.otp" type="text" placeholder="6-digit code" maxlength="6" required />
        </div>
        <div class="form-group">
          <label>New password</label>
          <input v-model="resetForm.newPassword" type="password" placeholder="New password" required />
        </div>
        <div class="form-group">
          <label>Confirm new password</label>
          <input v-model="resetForm.confirmPassword" type="password" placeholder="Confirm" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMsg" class="success-message">{{ successMsg }}</div>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Resetting...' : 'Reset password' }}
        </button>
        <p class="switch-text">
          <a href="#" @click.prevent="backToLogin">Back to login</a>
        </p>
      </form>
    </template>

    <p v-if="step === 'login'" class="switch-text">
      Don't have an account?
      <a href="#" @click.prevent="emit('switch-to-register')">Register here</a>
    </p>
  </div>
</template>

<style scoped>
.login-form {
  width: 100%;
}

h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--color-muted);
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: color-mix(in srgb, var(--color-heading) 85%, transparent);
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid color-mix(in srgb, var(--color-border) 85%, transparent);
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s;
  background: var(--color-surface);
  color: var(--color-text);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.forgot-link {
  margin-top: -0.5rem;
  margin-bottom: 1rem;
  text-align: right;
}

.forgot-link a {
  color: var(--color-primary);
  font-size: 0.9rem;
  text-decoration: none;
}

.forgot-link a:hover {
  text-decoration: underline;
}

.error-message {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.success-message {
  padding: 0.75rem 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  color: #16a34a;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.btn-submit {
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px color-mix(in srgb, var(--color-primary) 26%, transparent);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-text {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--color-muted);
  font-size: 0.95rem;
}

.switch-text a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}

.switch-text a:hover {
  text-decoration: underline;
}
</style>
