<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Login from './Login.vue'
import Register from './Register.vue'

const router = useRouter()

const token = localStorage.getItem('access_token')
if (token) router.replace('/dashboard')

const authMode = ref('') // '' | 'login' | 'register'
const showAuth = ref(false)

const openLogin = () => {
  authMode.value = 'login'
  showAuth.value = true
}
const openRegister = () => {
  authMode.value = 'register'
  showAuth.value = true
}
const closeAuth = () => {
  showAuth.value = false
  authMode.value = ''
}

const switchToRegister = () => { authMode.value = 'register' }
const switchToLogin = () => { authMode.value = 'login' }

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) closeAuth()
}

const handleEsc = (e) => {
  if (e.key === 'Escape' && showAuth.value) closeAuth()
}

const features = [
  { icon: '📊', title: 'Smart Dashboard', desc: 'Track attendance, grades, and progress all in one place.' },
  { icon: '💬', title: 'Live Chat', desc: 'Real-time messaging between students and faculty.' },
  { icon: '📅', title: 'Timetable', desc: 'Stay on top of your schedule with automatic updates.' },
  { icon: '🔔', title: 'Notifications', desc: 'Instant push alerts for announcements and deadlines.' },
  { icon: '📚', title: 'Resources', desc: 'Access study materials and documents anytime.' },
  { icon: '🛡️', title: 'Secure', desc: 'Enterprise-grade security for your data.' },
]

onMounted(() => document.addEventListener('keydown', handleEsc))
onBeforeUnmount(() => document.removeEventListener('keydown', handleEsc))
</script>

<template>
  <div class="home-page">
    <!-- Navbar -->
    <nav class="home-nav">
      <div class="nav-inner">
        <div class="nav-brand">
          <img src="../assets/mak-only.svg" alt="MAK Logo" class="nav-logo" />
          <span class="nav-title">MAK</span>
        </div>
        <div class="nav-actions">
          <button class="btn-nav-login" @click="openLogin">Login</button>
          <button class="btn-nav-register" @click="openRegister">Get Started</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg-orbs">
        <div class="orb orb-blue"></div>
        <div class="orb orb-teal"></div>
        <div class="orb orb-lime"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge">Digital Hub Platform</div>
        <img src="../assets/mak-only.svg" alt="MAK" class="hero-logo" />
        <h1 class="hero-title">
          Welcome to <span class="gradient-text">MAK</span>
        </h1>
        <p class="hero-subtitle">
          Your all-in-one college management platform. Attendance, grades, chat,
          schedules — everything you need, beautifully connected.
        </p>
        <div class="hero-buttons">
          <button class="btn-hero-primary" @click="openRegister">
            Create Account
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
          <button class="btn-hero-secondary" @click="openLogin">
            Sign In
          </button>
        </div>
        <p class="hero-note">Free for all MAK students and faculty</p>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="features-header">
        <h2>Everything You Need</h2>
        <p>Powerful tools designed for the modern campus experience</p>
      </div>
      <div class="features-grid">
        <div v-for="(f, i) in features" :key="i" class="feature-card">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-card">
        <h2>Ready to get started?</h2>
        <p>Join hundreds of students and faculty already using MAK.</p>
        <div class="cta-buttons">
          <button class="btn-hero-primary" @click="openRegister">
            Register Now
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
          <button class="btn-hero-secondary" @click="openLogin">Sign In</button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer">
      <img src="../assets/mak-only.svg" alt="MAK" class="footer-logo" />
      <p>&copy; 2026 MAK Digital Hub. All rights reserved.</p>
    </footer>

    <!-- Auth Modal Overlay -->
    <Transition name="overlay">
      <div v-if="showAuth" class="auth-overlay" @click="handleOverlayClick">
        <Transition name="modal" mode="out-in">
          <div class="auth-modal" :key="authMode">
            <button class="auth-close" @click="closeAuth" aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
            <div class="auth-modal-logo">
              <img src="../assets/mak-only.svg" alt="MAK" />
            </div>
            <Login
              v-if="authMode === 'login'"
              @close="closeAuth"
              @switch-to-register="switchToRegister"
            />
            <Register
              v-else-if="authMode === 'register'"
              @close="closeAuth"
              @switch-to-login="switchToLogin"
              @verify-email="switchToLogin"
            />
          </div>
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ==================== VARIABLES ==================== */
.home-page {
  --blue: #2080FF;
  --cyan: #00AACC;
  --teal: #00BF80;
  --green: #33CC66;
  --lime: #AADD00;
  --lime-bright: #CCFF33;
  --dark: #0f172a;
  --muted: #64748b;
  --light-bg: #f0fdf9;
  --surface: #ffffff;

  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--light-bg);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ==================== NAVBAR ==================== */
.home-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 191, 128, 0.15);
  box-shadow: 0 1px 12px rgba(0, 191, 128, 0.06);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.nav-logo {
  height: 34px;
  width: auto;
}

.nav-title {
  font-size: 1.35rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--blue), var(--teal));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.nav-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-nav-login {
  padding: 0.5rem 1.25rem;
  border: 2px solid var(--blue);
  border-radius: 10px;
  background: transparent;
  color: var(--blue);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav-login:hover {
  background: var(--blue);
  color: white;
  box-shadow: 0 4px 16px rgba(32, 128, 255, 0.25);
}

.btn-nav-register {
  padding: 0.55rem 1.35rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--blue), var(--teal));
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav-register:hover {
  box-shadow: 0 6px 20px rgba(32, 128, 255, 0.35);
  transform: translateY(-1px);
}

/* ==================== HERO ==================== */
.hero {
  position: relative;
  padding: 140px 1.5rem 80px;
  text-align: center;
  overflow: hidden;
}

.hero-bg-orbs {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.18;
}

.orb-blue {
  width: 500px;
  height: 500px;
  background: var(--blue);
  top: -120px;
  left: -100px;
  animation: float-orb 14s ease-in-out infinite;
}

.orb-teal {
  width: 400px;
  height: 400px;
  background: var(--teal);
  bottom: -80px;
  right: -60px;
  animation: float-orb 18s ease-in-out infinite reverse;
}

.orb-lime {
  width: 300px;
  height: 300px;
  background: var(--lime);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float-orb 12s ease-in-out infinite 3s;
}

@keyframes float-orb {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-40px) scale(1.08); }
}

.orb-lime {
  animation-name: float-orb-center;
}

@keyframes float-orb-center {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, calc(-50% - 30px)) scale(1.06); }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 720px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-block;
  padding: 0.35rem 1rem;
  border-radius: 100px;
  background: rgba(32, 128, 255, 0.08);
  border: 1px solid rgba(32, 128, 255, 0.2);
  color: var(--blue);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}

.hero-logo {
  height: 72px;
  width: auto;
  margin-bottom: 1.25rem;
  filter: drop-shadow(0 4px 20px rgba(32, 128, 255, 0.18));
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 900;
  color: var(--dark);
  line-height: 1.15;
  margin-bottom: 1rem;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(135deg, var(--blue), var(--teal), var(--lime));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.15rem;
  color: var(--muted);
  line-height: 1.7;
  max-width: 560px;
  margin: 0 auto 2rem;
}

.hero-buttons {
  display: flex;
  gap: 0.85rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 2rem;
  background: linear-gradient(135deg, var(--blue), var(--teal));
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 20px rgba(32, 128, 255, 0.25);
}

.btn-hero-primary:hover {
  box-shadow: 0 8px 32px rgba(32, 128, 255, 0.4);
  transform: translateY(-2px);
}

.btn-hero-secondary {
  padding: 0.85rem 2rem;
  background: var(--surface);
  color: var(--dark);
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-hero-secondary:hover {
  border-color: var(--blue);
  color: var(--blue);
  box-shadow: 0 4px 16px rgba(32, 128, 255, 0.12);
}

.hero-note {
  margin-top: 1.25rem;
  font-size: 0.85rem;
  color: var(--muted);
}

/* ==================== FEATURES ==================== */
.features-section {
  padding: 80px 1.5rem;
  max-width: 1100px;
  margin: 0 auto;
}

.features-header {
  text-align: center;
  margin-bottom: 3rem;
}

.features-header h2 {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--dark);
  margin-bottom: 0.6rem;
}

.features-header p {
  font-size: 1.05rem;
  color: var(--muted);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.feature-card {
  background: var(--surface);
  border: 1px solid rgba(0, 191, 128, 0.12);
  border-radius: 16px;
  padding: 2rem 1.5rem;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(32, 128, 255, 0.1);
  border-color: rgba(32, 128, 255, 0.25);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 0.85rem;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(32, 128, 255, 0.06);
  border-radius: 12px;
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 0.45rem;
}

.feature-card p {
  font-size: 0.92rem;
  color: var(--muted);
  line-height: 1.6;
}

/* ==================== CTA ==================== */
.cta-section {
  padding: 40px 1.5rem 80px;
  max-width: 800px;
  margin: 0 auto;
}

.cta-card {
  background: linear-gradient(135deg, var(--blue), var(--teal));
  border-radius: 24px;
  padding: 3.5rem 2.5rem;
  text-align: center;
  box-shadow: 0 16px 48px rgba(32, 128, 255, 0.2);
}

.cta-card h2 {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  margin-bottom: 0.6rem;
}

.cta-card p {
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.05rem;
  margin-bottom: 2rem;
}

.cta-buttons {
  display: flex;
  gap: 0.85rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-buttons .btn-hero-primary {
  background: white;
  color: var(--blue);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.cta-buttons .btn-hero-primary:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
  transform: translateY(-2px);
}

.cta-buttons .btn-hero-secondary {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
}

.cta-buttons .btn-hero-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.7);
  color: white;
}

/* ==================== FOOTER ==================== */
.home-footer {
  padding: 2.5rem 1.5rem;
  text-align: center;
  border-top: 1px solid rgba(0, 191, 128, 0.12);
}

.footer-logo {
  height: 36px;
  width: auto;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.home-footer p {
  font-size: 0.85rem;
  color: var(--muted);
}

/* ==================== AUTH MODAL ==================== */
.auth-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.auth-modal {
  position: relative;
  background: var(--surface);
  border-radius: 20px;
  padding: 2.5rem 2rem 2rem;
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.18);
}

.auth-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  cursor: pointer;
  color: var(--muted);
  transition: all 0.2s;
}

.auth-close:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--dark);
}

.auth-modal-logo {
  text-align: center;
  margin-bottom: 1.25rem;
}

.auth-modal-logo img {
  height: 44px;
  width: auto;
}

/* ==================== TRANSITIONS ==================== */
.overlay-enter-active { transition: opacity 0.25s ease; }
.overlay-leave-active { transition: opacity 0.2s ease; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }

.modal-enter-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from { opacity: 0; transform: translateY(16px) scale(0.97); }
.modal-leave-to { opacity: 0; transform: translateY(-8px) scale(0.98); }

/* ==================== RESPONSIVE ==================== */
@media (max-width: 900px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}



@media (max-width: 640px) {
  .hero-title {
    font-size: 2.2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-logo {
    height: 56px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .features-header h2 {
    font-size: 1.6rem;
  }

  .cta-card {
    padding: 2.5rem 1.5rem;
  }

  .cta-card h2 {
    font-size: 1.5rem;
  }

  .auth-modal {
    padding: 2rem 1.25rem 1.5rem;
    border-radius: 16px;
    max-width: 100%;
  }

  .nav-title {
    display: none;
  }

  .btn-nav-login {
    padding: 0.45rem 0.85rem;
    font-size: 0.82rem;
  }

  .btn-nav-register {
    padding: 0.45rem 1rem;
    font-size: 0.82rem;
  }
}
</style>
