<script setup>
import { ref } from 'vue'
import { authService } from '../services/api'

const emit = defineEmits(['close', 'switch-to-login', 'verify-email'])

const step = ref(1)

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
      setTimeout(() => emit('switch-to-login'), 2000)
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
  <div class="auth-form auth-register">
    <div v-if="step === 1">
      <h2>Create Account</h2>
      <p class="auth-sub">Join MAK as a student</p>

      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>User ID / Roll Number *</label>
          <input v-model="form.userid" type="text" placeholder="e.g. 21KB1A3029" required />
        </div>

        <div class="field-row">
          <div class="field">
            <label>First Name *</label>
            <input v-model="form.first_name" type="text" placeholder="First name" required />
          </div>
          <div class="field">
            <label>Last Name *</label>
            <input v-model="form.last_name" type="text" placeholder="Last name" required />
          </div>
        </div>

        <div class="field">
          <label>Phone Number *</label>
          <input v-model="form.phone" type="tel" placeholder="Enter phone number" required />
        </div>

        <div class="field">
          <label>Email *</label>
          <input v-model="form.email" type="email" placeholder="Enter your email" required />
        </div>

        <div class="field-row">
          <div class="field">
            <label>Password *</label>
            <input v-model="form.password" type="password" placeholder="Password" required />
          </div>
          <div class="field">
            <label>Confirm Password *</label>
            <input v-model="form.confirm_password" type="password" placeholder="Confirm" required />
          </div>
        </div>

        <div v-if="error" class="msg msg-error">{{ error }}</div>
        <div v-if="successMessage" class="msg msg-success">{{ successMessage }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p class="auth-switch">
        Already have an account?
        <a href="#" @click.prevent="emit('switch-to-login')">Login here</a>
      </p>
    </div>

    <div v-if="step === 2">
      <h2>Verify Email</h2>
      <p class="auth-sub">Enter the OTP sent to {{ verifyForm.email }}</p>

      <form @submit.prevent="handleVerifyOTP">
        <div class="field">
          <label>OTP Code *</label>
          <input
            v-model="verifyForm.otp"
            type="text"
            placeholder="Enter 6-digit OTP"
            maxlength="6"
            required
          />
        </div>

        <div v-if="error" class="msg msg-error">{{ error }}</div>
        <div v-if="successMessage" class="msg msg-success">{{ successMessage }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Verifying...' : 'Verify OTP' }}
        </button>
        <button type="button" class="btn-secondary" :disabled="resendOtpLoading" @click="handleResendOtp">
          {{ resendOtpLoading ? 'Sending...' : 'Resend OTP' }}
        </button>
      </form>

      <p class="auth-switch">
        <a href="#" @click.prevent="step = 1">Back to registration</a>
      </p>
    </div>
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

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.btn-secondary {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  color: #0f172a;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #2080FF;
  color: #2080FF;
}

.btn-secondary:disabled {
  opacity: 0.6;
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

@media (max-width: 480px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
