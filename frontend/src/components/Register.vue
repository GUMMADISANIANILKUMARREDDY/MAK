<script setup>
import { ref } from 'vue'
import { authService } from '../services/api'

const emit = defineEmits(['close', 'switch-to-login', 'verify-email'])

const step = ref(1) // 1 = register, 2 = verify OTP

const form = ref({
  userid: '',
  first_name: '',
  last_name: '',
  phone: '',
  email: '',
  password: '',
  confirm_password: '',
})

const verifyForm = ref({
  email: '',
  otp: '',
})

const loading = ref(false)
const error = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  error.value = ''
  successMessage.value = ''
  loading.value = true

  if (form.value.password !== form.value.confirm_password) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }

  try {
    const response = await authService.register(form.value)

    if (response.success) {
      successMessage.value = response.message
      verifyForm.value.email = form.value.email
      step.value = 2
    } else {
      error.value = response.message || 'Registration failed'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleVerifyOTP = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await authService.verifyEmail(verifyForm.value.email, verifyForm.value.otp)

    if (response.success) {
      successMessage.value = 'Email verified! Redirecting to login...'
      setTimeout(() => {
        emit('switch-to-login')
      }, 2000)
    } else {
      error.value = response.message || 'Verification failed'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Verification failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const resendOtpLoading = ref(false)
const handleResendOtp = async () => {
  error.value = ''
  successMessage.value = ''
  resendOtpLoading.value = true
  try {
    const response = await authService.resendOtp(verifyForm.value.email)
    if (response.success) {
      successMessage.value = response.message || 'New OTP sent. Check your email.'
    } else {
      error.value = response.message || 'Failed to resend OTP'
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to resend OTP. Try again.'
  } finally {
    resendOtpLoading.value = false
  }
}
</script>

<template>
  <div class="register-form">
    <!-- Step 1: Register -->
    <div v-if="step === 1">
      <h2>Create Account</h2>
      <p class="subtitle">Join MAK as a student</p>

      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="form-group">
            <label>User ID / Roll Number*</label>
            <input v-model="form.userid" type="text" placeholder="e.g. 21KB1A3029" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>First Name*</label>
            <input v-model="form.first_name" type="text" placeholder="First name" required />
          </div>
          <div class="form-group">
            <label>Last Name*</label>
            <input v-model="form.last_name" type="text" placeholder="Last name" required />
          </div>
        </div>

        <div class="form-group">
          <label>Phone Number*</label>
          <input v-model="form.phone" type="tel" placeholder="Enter phone number" required />
        </div>

        <div class="form-group">
          <label>Email*</label>
          <input v-model="form.email" type="email" placeholder="Enter your email" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Password*</label>
            <input v-model="form.password" type="password" placeholder="Password" required />
          </div>
          <div class="form-group">
            <label>Confirm Password*</label>
            <input
              v-model="form.confirm_password"
              type="password"
              placeholder="Confirm password"
              required
            />
          </div>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p class="switch-text">
        Already have an account?
        <a href="#" @click.prevent="emit('switch-to-login')">Login here</a>
      </p>
    </div>

    <!-- Step 2: Verify OTP -->
    <div v-if="step === 2">
      <h2>Verify Email</h2>
      <p class="subtitle">Enter the OTP sent to {{ verifyForm.email }}</p>

      <form @submit.prevent="handleVerifyOTP">
        <div class="form-group">
          <label>OTP Code*</label>
          <input
            v-model="verifyForm.otp"
            type="text"
            placeholder="Enter 6-digit OTP"
            maxlength="6"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Verifying...' : 'Verify OTP' }}
        </button>
        <button type="button" class="btn-secondary" :disabled="resendOtpLoading" @click="handleResendOtp">
          {{ resendOtpLoading ? 'Sending...' : 'Resend OTP' }}
        </button>
      </form>

      <p class="switch-text">
        <a href="#" @click.prevent="step = 1">Back to registration</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-form {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
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
  background: var(--color-danger-bg);
  border: 1px solid color-mix(in srgb, var(--color-danger) 32%, transparent);
  border-radius: 8px;
  color: var(--color-danger);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.success-message {
  padding: 0.75rem 1rem;
  background: var(--color-success-bg);
  border: 1px solid color-mix(in srgb, var(--color-success) 28%, transparent);
  border-radius: 8px;
  color: var(--color-success);
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
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px color-mix(in srgb, var(--color-primary) 24%, transparent);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 2px solid var(--color-border);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-secondary:disabled {
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

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
