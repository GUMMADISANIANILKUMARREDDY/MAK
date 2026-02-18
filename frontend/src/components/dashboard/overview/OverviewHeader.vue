<script setup>
import { computed } from 'vue'

defineProps({
  username: { type: String, default: '' },
  subtitle: { type: String, default: "Here's what's happening with your dashboard today." }
})

const timeGreeting = computed(() => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return 'Good morning'
  if (hour >= 12 && hour < 17) return 'Good afternoon'
  return 'Good evening'
})
</script>

<template>
  <div class="overview-header-wrapper">
    <div class="overview-header d-flex align-items-center mb-4">
      <div class="overview-welcome-block">
        <h2 class="overview-welcome mb-1">{{ timeGreeting }}, {{ username }}!</h2>
        <p class="overview-subtitle text-muted mb-0">{{ subtitle }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overview-header-wrapper {
  padding: 0.5rem 0 1rem 0;
}

.overview-header {
  padding: 1rem 1.25rem;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.overview-welcome {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.overview-subtitle {
  font-size: 0.95rem;
}
</style>
