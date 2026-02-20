<script setup>
import { ref } from 'vue'
import Login from './Login.vue'
import Register from './Register.vue'
const menuOpen = ref(false)
const showAuthModal = ref(false)
const authMode = ref('login') // 'login' or 'register'

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const openLoginModal = () => {
  authMode.value = 'login'
  showAuthModal.value = true
  menuOpen.value = false
}

const openRegisterModal = () => {
  authMode.value = 'register'
  showAuthModal.value = true
  menuOpen.value = false
}

const closeModal = () => {
  showAuthModal.value = false
}

const switchToLogin = () => {
  authMode.value = 'login'
}

const switchToRegister = () => {
  authMode.value = 'register'
}

const stats = ref([
  { value: '500+', label: 'Students Trained', color: 'orange', icon: '◆' },
  { value: '50+', label: 'Hackathons Conducted', color: 'green', icon: '◇' },
  { value: '100+', label: 'Industry Experts', color: 'blue', icon: '★' },
  { value: '200+', label: 'Projects Guided', color: 'teal', icon: '●' },
])

const contextData = ref([
  {
    title: 'Real-time experience',
    description: 'Learn by doing. We give you live, hands-on training with industry experts, just real-world practice.',
    icon: '◆',
    color: 'blue',
  },
  {
    title: 'Hackathons',
    description: 'Compete and collaborate in hackathons we conduct. Build projects, get feedback, and grow with peers.',
    icon: '◇',
    color: 'green',
  },
  {
    title: 'Industry experts',
    description: 'Training led by professionals from the industry. Get real-time guidance on how to develop and ship projects.',
    icon: '★',
    color: 'orange',
  },
  {
    title: 'Project guidance & licence',
    description: 'We guide you on how to develop projects and provide project licences. You learn the process, not just the outcome.',
    icon: '●',
    color: 'teal',
  },
])

const moreActions = ref([
  { label: 'Programs & Experiences', href: '#programs', variant: 'primary', icon: '→' },
  { label: 'Hackathons', href: '#hackathons', variant: 'outline', icon: '›' },
  { label: 'About MAK', href: '#about', variant: 'outline', icon: '✉' },
  { label: 'Contact', href: '#contact', variant: 'outline', icon: '✉' },
  { label: 'Create Account', action: 'register', variant: 'secondary', icon: '★' },
])
</script>

<template>
  <div class="home">
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-container">
        <a href="/home" class="nav-logo">
          <img class="logo-img" src="/mak-only.svg?v=2" alt="MAK" />
          <span class="nav-logo-text">MAK Technologies</span>
        </a>

        <!-- Hamburger button - visible on small screens -->
        <button
          class="hamburger"
          aria-label="Toggle menu"
          :class="{ 'hamburger-open': menuOpen }"
          @click="toggleMenu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <!-- Desktop nav links and actions -->
        <ul class="nav-links">
          <li><a href="#hero" @click="menuOpen = false">Home</a></li>
          <li><a href="#programs" @click="menuOpen = false">Programs</a></li>
          <li><a href="#hackathons" @click="menuOpen = false">Hackathons</a></li>
          <li><a href="#about" @click="menuOpen = false">About</a></li>
          <li><a href="#contact" @click="menuOpen = false">Contact</a></li>
        </ul>
        <div class="nav-actions">
          <button @click="openLoginModal" class="btn-nav btn-login">Login</button>
          <button @click="openRegisterModal" class="btn-nav btn-register">Register</button>
        </div>
      </div>

      <!-- Mobile dropdown menu -->
      <div class="nav-dropdown" :class="{ 'nav-dropdown-open': menuOpen }">
        <ul class="nav-dropdown-links">
          <li><a href="#hero" @click="toggleMenu">Home</a></li>
          <li><a href="#programs" @click="toggleMenu">Programs</a></li>
          <li><a href="#hackathons" @click="toggleMenu">Hackathons</a></li>
          <li><a href="#about" @click="toggleMenu">About</a></li>
          <li><a href="#contact" @click="toggleMenu">Contact</a></li>
          <li><a href="#technologies" @click="toggleMenu">Technologies</a></li>
        </ul>
        <div class="nav-dropdown-actions">
          <button @click="openLoginModal" class="btn-nav btn-login">Login</button>
          <button @click="openRegisterModal" class="btn-nav btn-register">Register</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="hero" class="hero">
      <div class="hero-bg">
        <div class="hero-blob hero-blob-1"></div>
        <div class="hero-blob hero-blob-2"></div>
        <div class="hero-blob hero-blob-3"></div>
        <div class="hero-pattern"></div>
      </div>
      <div class="hero-content">
        <span class="hero-badge">Real-Time Experience & Hackathons</span>
        <h1>Train with <span class="gradient-text">Industry Experts</span></h1>
        <p class="hero-subtitle">
          We give students real-time experience and run hackathons. Learn how to develop projects
          with guidance from industry experts—we guide you; we do not provide placements.
        </p>
        <div class="hero-buttons">
          <a href="#programs" class="btn btn-primary">Programs & Experiences</a>
          <a href="#hackathons" class="btn btn-outline">Hackathons</a>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
      <div class="stats-container">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="stat-card"
          :class="`stat-${stat.color}`"
        >
          <span class="stat-icon">{{ stat.icon }}</span>
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <!-- Programs section (nav scrolls here on same page) -->
    <section id="programs" class="extra-section programs-section">
      <div class="extra-container">
        <h2 class="extra-heading">Programs & real-time experience</h2>
        <p class="extra-lead">
          Join live programs where you train with industry experts. Real-time experience only—no placements. We guide you on how to develop and ship projects.
        </p>
        <ul class="extra-list">
          <li>Live workshops and hands-on sessions</li>
          <li>Project guidance and development process</li>
          <li>Project licence and best practices</li>
        </ul>
      </div>
    </section>

    <!-- More context section -->
    <section id="about" class="context-section">
      <div class="context-container">
        <h2 class="context-heading">Why MAK?</h2>
        <p class="context-lead">
          Real-time experience with industry experts, hackathons, and project guidance—we train you how to develop; we do not offer placements.
        </p>
        <div class="context-grid">
          <div
            v-for="(item, index) in contextData"
            :key="index"
            class="context-card"
            :class="`context-${item.color}`"
          >
            <span class="context-icon">{{ item.icon }}</span>
            <h3 class="context-title">{{ item.title }}</h3>
            <p class="context-desc">{{ item.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Hackathons section (nav scrolls here on same page) -->
    <section id="hackathons" class="extra-section hackathons-section">
      <div class="extra-container">
        <h2 class="extra-heading">Hackathons we conduct</h2>
        <p class="extra-lead">
          We run hackathons so you can build, compete, and learn with peers. Get feedback from industry experts and improve your real-world skills.
        </p>
        <ul class="extra-list">
          <li>Regular hackathons across domains</li>
          <li>Mentorship and judging by industry experts</li>
          <li>Prizes and recognition for top projects</li>
        </ul>
      </div>
    </section>

    <!-- More actions section -->
    <section class="actions-section">
      <div class="actions-container">
        <h2 class="actions-heading">Get started</h2>
        <p class="actions-lead">Join programs, hackathons, or create your account to access real-time training and project guidance.</p>
        <div class="actions-grid">
          <template v-for="(action, index) in moreActions" :key="index">
            <a
              v-if="action.href"
              :href="action.href"
              class="action-btn"
              :class="`action-${action.variant}`"
            >
              <span class="action-label">{{ action.label }}</span>
              <span class="action-icon">{{ action.icon }}</span>
            </a>
            <button
              v-else
              type="button"
              class="action-btn"
              :class="`action-${action.variant}`"
              @click="openRegisterModal"
            >
              <span class="action-label">{{ action.label }}</span>
              <span class="action-icon">{{ action.icon }}</span>
            </button>
          </template>
        </div>
      </div>
    </section>

    <!-- Technologies section (nav scrolls here on same page) -->
    <section id="technologies" class="extra-section technologies-section">
      <div class="extra-container">
        <h2 class="extra-heading">Technologies</h2>
        <p class="extra-lead">
          We work with modern tools and stacks so you get real-time experience with industry-relevant technologies.
        </p>
        <ul class="extra-list">
          <li>Web & mobile development</li>
          <li>Cloud and DevOps</li>
          <li>Data and APIs</li>
        </ul>
      </div>
    </section>

    <!-- Contact section (nav scrolls here on same page) -->
    <section id="contact" class="extra-section contact-section">
      <div class="extra-container">
        <h2 class="extra-heading">Contact us</h2>
        <p class="extra-lead">
          Have questions about programs, hackathons, or project guidance? Reach out and we’ll get back to you.
        </p>
        <div class="contact-block">
          <p class="contact-text">Email: <a href="mailto:contact@mak.example.com" class="contact-link">contact@mak.example.com</a></p>
          <p class="contact-text">Follow us for updates on upcoming hackathons and programs.</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-brand">
          <img class="footer-logo" src="/mak-only.svg?v=2" alt="MAK" />
          <p class="footer-tagline">Real-time experience & hackathons. We guide; we don’t place.</p>
        </div>
        <nav class="footer-nav" aria-label="Footer navigation">
          <a href="#hero">Home</a>
          <a href="#programs">Programs</a>
          <a href="#hackathons">Hackathons</a>
          <a href="#about">About</a>
          <a href="#technologies">Technologies</a>
          <a href="#contact">Contact</a>
        </nav>
        <div class="footer-bottom">
          <p class="footer-copy">&copy; {{ new Date().getFullYear() }} MAK. All rights reserved.</p>
        </div>
      </div>
    </footer>

    <!-- Auth Modal (Login/Register Popup) -->
    <div v-if="showAuthModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeModal">&times;</button>
        <Login v-if="authMode === 'login'" @close="closeModal" @switch-to-register="switchToRegister" />
        <Register v-else @close="closeModal" @switch-to-login="switchToLogin" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* MAK brand color palette (from logo) */
.home {
  --orange: #AADD00; /* MAK lime */
  --orange-glow: rgba(170, 221, 0, 0.35);
  --orange-soft: #e8ffcc;
  --green: #33CC66; /* MAK green */
  --green-glow: rgba(51, 204, 102, 0.35);
  --green-soft: #e6faf0;
  --blue: #2080FF; /* MAK blue */
  --blue-glow: rgba(32, 128, 255, 0.32);
  --blue-soft: #e6f2ff;
  --teal: #00BF80; /* MAK teal */
  --teal-glow: rgba(0, 191, 128, 0.28);
  --teal-soft: #e0faf5;
  --cyan: #00AACC; /* MAK cyan */
  --white: #ffffff;
  --slate: #1e293b;
  --slate-muted: #64748b;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  min-height: 100vh;
}

/* Navigation - fixed everywhere, never scrolls away */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: linear-gradient(120deg, #ffffff 0%, #e0faf5 35%, #e8ffcc 70%, #e6f2ff 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 191, 128, 0.2);
  box-shadow: 0 4px 24px rgba(0, 170, 204, 0.08);
}

/* Reserve space so content is not under fixed nav */
.home {
  padding-top: 72px;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-logo {
  font-weight: 800;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: -0.5px;
  padding: 0 !important; /* override global <a> padding */
  border-radius: 0 !important;
  background: transparent !important;
  cursor: pointer;
}

.nav-logo:hover,
.nav-logo:focus,
.nav-logo:active {
  background: transparent !important; /* remove blue hover square */
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 2.5rem;
  margin: 0;
  padding: 0;
  align-items: center;
}

.logo-img {
  width: 140px;
  height: 62px;
  display: block;
  object-fit: contain;
}

.nav-logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.25rem;
  letter-spacing: -0.02em;
  white-space: nowrap;
  background: linear-gradient(135deg, var(--blue), var(--teal), var(--orange));
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: #0f172a; /* fallback if gradient not supported */
}

.nav-links a {
  color: #0f172a;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  position: relative;
  padding: 0 !important; /* override global <a> padding */
  border-radius: 0 !important;
  background: transparent !important;
  cursor: pointer;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--teal), var(--blue), var(--orange));
  transition: width 0.3s ease;
}

.nav-links a:hover::after {
  width: 100%;
}

.nav-links a:hover {
  color: var(--blue);
  background: transparent !important; /* remove blue hover square */
}

.nav-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-nav {
  padding: 0.5rem 1.25rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.3s ease;
  white-space: nowrap;
  cursor: pointer;
  border: none;
  font-family: inherit;
}

.btn-login {
  color: var(--blue);
  background: transparent;
  border: 2px solid var(--blue);
}

.btn-login:hover {
  background: var(--blue);
  color: var(--white);
}

.btn-register {
  background: linear-gradient(135deg, var(--blue), var(--teal));
  color: var(--white);
  border: 2px solid transparent;
}

.btn-register:hover {
  box-shadow: 0 10px 26px rgba(32, 128, 255, 0.3);
}

/* Hamburger button - hidden on desktop */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  width: 44px;
  height: 44px;
  padding: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.hamburger span {
  display: block;
  width: 24px;
  height: 2.5px;
  background: var(--blue);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger:hover {
  background: rgba(32, 128, 255, 0.12);
}

.hamburger-open span:nth-child(1) {
  transform: translateY(8.5px) rotate(45deg);
}

.hamburger-open span:nth-child(2) {
  opacity: 0;
}

.hamburger-open span:nth-child(3) {
  transform: translateY(-8.5px) rotate(-45deg);
}

/* Mobile dropdown */
.nav-dropdown {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, #ffffff 0%, #e0faf5 40%, #e8ffcc 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 191, 128, 0.2);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.35s ease, opacity 0.3s ease;
}

.nav-dropdown-open {
  max-height: 320px;
  opacity: 1;
}

.nav-dropdown-links {
  list-style: none;
  margin: 0;
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-dropdown-links a {
  display: block;
  padding: 0.75rem 1rem;
  color: #0f172a;
  text-decoration: none;
  font-weight: 600;
  border-radius: 8px;
  transition: background 0.2s;
}

.nav-dropdown-links a:hover {
  background: rgba(32, 128, 255, 0.12);
  color: var(--blue);
}

.nav-dropdown-actions {
  display: flex;
  gap: 0.75rem;
  padding: 0 1.5rem 1.5rem;
}

.nav-dropdown-actions .btn-nav {
  flex: 1;
  justify-content: center;
  text-align: center;
}

/* Hero Section */
.hero {
  position: relative;
  padding: 6rem 2rem 7rem;
  overflow: hidden;
  min-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    160deg,
    #e6f2ff 0%,
    #e0faf5 25%,
    #e6faf0 50%,
    #e8ffcc 75%,
    #e6f2ff 100%
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;
}

.hero-blob-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, var(--blue-glow), var(--teal-glow));
  top: -150px;
  right: -100px;
  animation-delay: 0s;
}

.hero-blob-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, var(--orange-glow), #e8ffcc);
  bottom: -100px;
  left: -100px;
  animation-delay: -7s;
}

.hero-blob-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, var(--green-glow), var(--blue-glow));
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(32, 128, 255, 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
}

.hero-content {
  position: relative;
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: linear-gradient(135deg, rgba(32, 128, 255, 0.14), rgba(0, 191, 128, 0.12));
  border: 1px solid rgba(32, 128, 255, 0.25);
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--blue);
  margin-bottom: 1.5rem;
  letter-spacing: 0.5px;
  animation: fadeInUp 0.8s ease;
}

.hero h1 {
  font-size: 3rem;
  font-weight: 800;
  color: var(--slate);
  margin-bottom: 1.25rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  animation: fadeInUp 0.8s ease 0.1s both;
}

.gradient-text {
  background: linear-gradient(135deg, var(--blue), var(--teal), var(--orange));
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 4s linear infinite;
}

@keyframes shimmer {
  to { background-position: 200% center; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--slate-muted);
  line-height: 1.75;
  margin-bottom: 2rem;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeInUp 0.8s ease 0.2s both;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  animation: fadeInUp 0.8s ease 0.3s both;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.9rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--blue), var(--teal));
  color: var(--white);
  box-shadow: 0 12px 26px rgba(32, 128, 255, 0.25);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 36px rgba(32, 128, 255, 0.3);
}

.btn-outline {
  background: var(--white);
  color: var(--blue);
  border: 2px solid var(--blue);
}

.btn-outline:hover {
  background: var(--blue);
  color: var(--white);
  transform: translateY(-3px);
}

/* Stats Section */
.stats {
  position: relative;
  margin-top: -3rem;
  padding: 0 2rem 4rem;
  z-index: 10;
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(0, 0, 0, 0.03);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 20px 20px 0 0;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(0, 0, 0, 0.05);
}

.stat-orange {
  background: linear-gradient(180deg, #f7ffcc 0%, var(--white) 100%);
}

.stat-orange::before {
  background: linear-gradient(90deg, var(--orange), #CCFF33);
}

.stat-green {
  background: linear-gradient(180deg, #e6faf0 0%, var(--white) 100%);
}

.stat-green::before {
  background: linear-gradient(90deg, var(--green), #66CC33);
}

.stat-blue {
  background: linear-gradient(180deg, #e6f2ff 0%, var(--white) 100%);
}

.stat-blue::before {
  background: linear-gradient(90deg, var(--blue), #00AACC);
}

.stat-teal {
  background: linear-gradient(180deg, #e0faf5 0%, var(--white) 100%);
}

.stat-teal::before {
  background: linear-gradient(90deg, var(--teal), #33CC66);
}

.stat-icon {
  display: block;
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
  opacity: 0.9;
}

.stat-orange .stat-icon { color: var(--orange); }
.stat-green .stat-icon { color: var(--green); }
.stat-blue .stat-icon { color: var(--blue); }
.stat-teal .stat-icon { color: var(--teal); }

.stat-value {
  display: block;
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.stat-orange .stat-value { color: var(--orange); }
.stat-green .stat-value { color: var(--green); }
.stat-blue .stat-value { color: var(--blue); }
.stat-teal .stat-value { color: var(--teal); }

.stat-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--slate-muted);
}

/* More context section */
.context-section {
  padding: 4rem 2rem 5rem;
  background: linear-gradient(180deg, #f0fdf9 0%, #e6f2ff 50%, #f0fdf9 100%);
}

.context-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.context-heading {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--slate);
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.context-lead {
  font-size: 1.15rem;
  color: var(--slate-muted);
  max-width: 560px;
  margin: 0 auto 3rem;
  line-height: 1.7;
}

.context-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  text-align: left;
}

.context-card {
  padding: 2rem;
  border-radius: 20px;
  background: var(--white);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.35s ease;
}

.context-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
}

.context-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 20px 20px 0 0;
}

.context-card {
  position: relative;
}

.context-blue::before { background: linear-gradient(90deg, var(--blue), #00AACC); }
.context-green::before { background: linear-gradient(90deg, var(--green), #66CC33); }
.context-orange::before { background: linear-gradient(90deg, var(--orange), #CCFF33); }
.context-teal::before { background: linear-gradient(90deg, var(--teal), #33CC66); }

.context-icon {
  display: block;
  font-size: 1.75rem;
  margin-bottom: 1rem;
}

.context-blue .context-icon { color: var(--blue); }
.context-green .context-icon { color: var(--green); }
.context-orange .context-icon { color: var(--orange); }
.context-teal .context-icon { color: var(--teal); }

.context-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--slate);
  margin-bottom: 0.5rem;
}

.context-desc {
  font-size: 0.95rem;
  color: var(--slate-muted);
  line-height: 1.6;
  margin: 0;
}

/* More actions section */
.actions-section {
  padding: 3rem 2rem 5rem;
  background: linear-gradient(180deg, #e6f2ff 0%, #e0faf5 100%);
}

.actions-container {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}

.actions-heading {
  font-size: 2rem;
  font-weight: 800;
  color: var(--slate);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.actions-lead {
  font-size: 1.05rem;
  color: var(--slate-muted);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.actions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.75rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  border: 2px solid transparent;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s ease;
}

.action-btn a {
  text-decoration: none;
  color: inherit;
}

.action-primary {
  background: linear-gradient(135deg, var(--blue), var(--teal));
  color: var(--white);
  box-shadow: 0 8px 24px rgba(32, 128, 255, 0.25);
}

.action-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(32, 128, 255, 0.3);
}

.action-outline {
  background: var(--white);
  color: var(--blue);
  border-color: var(--blue);
}

.action-outline:hover {
  background: var(--blue);
  color: var(--white);
  transform: translateY(-3px);
}

.action-secondary {
  background: linear-gradient(135deg, var(--orange), #CCFF33);
  color: var(--slate);
  border-color: transparent;
}

.action-secondary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(170, 221, 0, 0.35);
}

.action-icon {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* Extra sections: Programs, Hackathons, Contact (same-page nav targets) */
.extra-section {
  padding: 4rem 2rem;
  scroll-margin-top: 80px;
}

.extra-container {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.extra-heading {
  font-size: 2rem;
  font-weight: 800;
  color: var(--slate);
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.extra-lead {
  font-size: 1.1rem;
  color: var(--slate-muted);
  line-height: 1.7;
  margin-bottom: 1.5rem;
}

.extra-list {
  text-align: left;
  max-width: 420px;
  margin: 0 auto;
  padding-left: 1.25rem;
  color: var(--slate-muted);
  line-height: 1.8;
}

.programs-section {
  background: linear-gradient(180deg, #e6f2ff 0%, #ffffff 100%);
}

.hackathons-section {
  background: linear-gradient(180deg, #e0faf5 0%, #e6f2ff 100%);
}

.technologies-section {
  background: linear-gradient(180deg, #e6f2ff 0%, #e0faf5 100%);
}

.contact-section {
  background: linear-gradient(180deg, #e8ffcc 0%, #f0fdf9 100%);
}

.contact-block {
  margin-top: 1rem;
}

.contact-text {
  color: var(--slate-muted);
  margin-bottom: 0.5rem;
}

.contact-link {
  color: var(--blue);
  font-weight: 600;
  text-decoration: none;
  padding: 0 !important;
  background: transparent !important;
  border-radius: 0 !important;
}

.contact-link:hover {
  text-decoration: underline;
  background: transparent !important;
}

/* Footer */
.site-footer {
  background: var(--slate);
  color: var(--white);
  padding: 3rem 2rem 2rem;
  margin-top: 0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  margin-bottom: 1.5rem;
}

.footer-logo {
  width: 96px;
  height: 42px;
  display: block;
  margin: 0 auto 0.75rem;
  filter: brightness(0) invert(1);
}

.footer-tagline {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 360px;
  margin: 0 auto;
  line-height: 1.5;
}

.footer-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.25rem 2rem;
  margin-bottom: 2rem;
}

.footer-nav a {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0 !important;
  background: transparent !important;
  border-radius: 0 !important;
}

.footer-nav a:hover {
  color: var(--white);
  text-decoration: underline;
  background: transparent !important;
}

.footer-bottom {
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.footer-copy {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
  margin: 0;
}

/* Responsive - all devices */
@media (max-width: 1024px) {
  .nav-links {
    gap: 1.5rem;
  }
  .hero {
    padding: 5rem 1.5rem 6rem;
    min-height: 80vh;
  }
  .hero h1 {
    font-size: 2.75rem;
  }
  .hero-subtitle {
    font-size: 1.1rem;
  }
  .hero-blob-1 {
    width: 350px;
    height: 350px;
  }
  .hero-blob-2 {
    width: 280px;
    height: 280px;
  }
  .hero-blob-3 {
    width: 220px;
    height: 220px;
  }
  .stat-value {
    font-size: 2.25rem;
  }
  .context-heading {
    font-size: 2rem;
  }
  .context-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .actions-heading {
    font-size: 1.75rem;
  }
  .extra-section {
    padding: 3rem 1.5rem;
  }
  .extra-heading {
    font-size: 1.75rem;
  }
}

@media (min-width: 768px) {
  .hero h1 {
    font-size: 3.5rem;
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0.75rem 1rem;
    flex-wrap: nowrap;
  }
  .nav-logo {
    gap: 0.35rem;
  }
  .logo-img {
    width: 112px;
    height: 50px;
    object-fit: contain;
  }
  .nav-logo-text {
    font-size: 1rem;
  }
  .hamburger {
    display: flex;
    margin-left: auto;
  }
  .nav-links,
  .nav-actions {
    display: none;
  }
  .nav-dropdown {
    display: block;
  }
  .nav-logo {
    font-size: 1.25rem;
  }
  .hero {
    padding: 4rem 1rem 5rem;
    min-height: auto;
  }
  .hero h1 {
    font-size: 2.25rem;
  }
  .hero-subtitle {
    font-size: 1rem;
    margin-bottom: 1.5rem;
  }
  .hero-buttons {
    flex-direction: column;
  }
  .btn {
    width: 100%;
    justify-content: center;
  }
  .stats {
    margin-top: -2.5rem;
    padding: 0 1rem 3rem;
  }
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .stat-card {
    padding: 1.5rem 1rem;
  }
  .stat-value {
    font-size: 2rem;
  }
  .stat-label {
    font-size: 0.9rem;
  }
  .context-section {
    padding: 3rem 1rem 4rem;
  }
  .context-heading {
    font-size: 1.75rem;
  }
  .context-lead {
    margin-bottom: 2rem;
    font-size: 1rem;
  }
  .context-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .context-card {
    padding: 1.5rem;
  }
  .actions-section {
    padding: 2.5rem 1rem 4rem;
  }
  .actions-heading {
    font-size: 1.5rem;
  }
  .actions-lead {
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
  }
  .actions-grid {
    flex-direction: column;
  }
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  .extra-section {
    padding: 2.5rem 1rem;
  }
  .extra-heading {
    font-size: 1.5rem;
  }
  .extra-lead {
    font-size: 1rem;
  }
  .site-footer {
    padding: 2rem 1rem 1.5rem;
  }
  .footer-nav {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .btn-nav {
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
  }
  .hero h1 {
    font-size: 1.85rem;
  }
  .hero-badge {
    font-size: 0.75rem;
    padding: 0.35rem 0.75rem;
  }
  .stats-container {
    grid-template-columns: 1fr;
  }
  .context-heading {
    font-size: 1.5rem;
  }
  .actions-heading {
    font-size: 1.35rem;
  }
  .extra-heading {
    font-size: 1.35rem;
  }
}

/* Ensure fluid layout */
.home {
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
}

/* Auth Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--color-surface-2);
  color: var(--slate-muted);
  font-size: 1.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e2e8f0;
  color: #334155;
}



@media (max-width: 640px) {
  .modal-content {
    padding: 2rem 1.5rem;
    max-width: 95%;
  }
}
</style>
