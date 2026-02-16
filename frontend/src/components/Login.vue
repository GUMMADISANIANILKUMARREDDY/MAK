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

const handleLogin = async () => {
  error.value = ''
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
      if (response.user) {
        localStorage.setItem('user', JSON.stringify(response.user))
      } else {
        // Fallback if API returns token without user
        const me = await authService.getMe()
        localStorage.setItem('user', JSON.stringify(me))
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
</script>

<template>
  <div class="login-form">
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

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" class="btn-submit" :disabled="loading">
        <span>{{ loading ? 'Logging in...' : 'Login' }}</span>
      </button>
    </form>

    <p class="switch-text">
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

.error-message {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
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
