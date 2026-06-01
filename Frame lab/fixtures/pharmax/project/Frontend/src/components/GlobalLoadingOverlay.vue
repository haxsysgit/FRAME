<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { globalLoading } from '../services/globalLoading'

const progressWidth = computed(() => `${Math.max(0, Math.min(100, globalLoading.progress.value)).toFixed(1)}%`)
const totalInFlight = computed(() => globalLoading.totalActive.value)
const resourcesInFlight = computed(() => globalLoading.resourcesInFlight.value)
const detailsOpen = ref(false)
let staleResetTimer = null

function toggleDetails() {
  if (totalInFlight.value === 0) return
  detailsOpen.value = !detailsOpen.value
}

function closeDetails() {
  detailsOpen.value = false
}

function clearStaleResetTimer() {
  if (staleResetTimer) {
    clearTimeout(staleResetTimer)
    staleResetTimer = null
  }
}

function onDocumentClick() {
  closeDetails()
}

watch(totalInFlight, (next) => {
  if (next === 0) {
    closeDetails()
    clearStaleResetTimer()
    return
  }

  clearStaleResetTimer()
  staleResetTimer = window.setTimeout(() => {
    globalLoading.resetLoadingState()
    closeDetails()
  }, 25000)
})

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
  clearStaleResetTimer()
})
</script>

<template>
  <div class="global-progress" :class="{ show: globalLoading.visible.value }" aria-hidden="true">
    <div class="global-progress-bar" :style="{ width: progressWidth }" />

    <div class="global-progress-meta">
      <button
        v-if="totalInFlight > 0"
        type="button"
        class="global-progress-pill"
        @click.stop="toggleDetails"
      >
        <span class="pill-spinner" aria-hidden="true" />
        Loading {{ totalInFlight }} task{{ totalInFlight === 1 ? '' : 's' }}
      </button>

      <Transition name="global-loader-fade">
        <div v-if="detailsOpen && resourcesInFlight.length" class="global-progress-details" @click.stop>
          <p class="details-title">Please wait while we finish:</p>
          <ul>
            <li v-for="resource in resourcesInFlight" :key="resource.label">
              <span>{{ resource.label }}</span>
              <strong v-if="resource.count > 1">×{{ resource.count }}</strong>
            </li>
          </ul>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.global-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 1100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 120ms ease;
}

.global-progress.show {
  opacity: 1;
}

.global-progress-bar {
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  box-shadow: 0 0 10px var(--primary-tint);
  transition: width 180ms ease;
}

.global-progress-meta {
  position: fixed;
  top: 64px;
  right: 12px;
  pointer-events: auto;
  display: grid;
  gap: 8px;
  justify-items: end;
}

.global-progress-pill {
  border: 1px solid var(--primary-tint);
  background: var(--bg-card);
  color: var(--text-primary);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  padding: 7px 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: var(--shadow-md);
}

.pill-spinner {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  border: 2px solid var(--border-default);
  border-top-color: var(--primary);
  animation: spin-loader 0.7s linear infinite;
}

.global-progress-details {
  width: min(460px, calc(100vw - 20px));
  max-height: min(55vh, 420px);
  overflow: auto;
  border-radius: 10px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  box-shadow: var(--shadow-lg);
  padding: 12px;
}

.details-title {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.global-progress-details ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.global-progress-details li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--bg-recessed);
}

.global-progress-details strong {
  color: var(--text-primary);
}

.global-loader-fade-enter-active,
.global-loader-fade-leave-active {
  transition: opacity 140ms ease;
}

.global-loader-fade-enter-from,
.global-loader-fade-leave-to {
  opacity: 0;
}

@keyframes spin-loader {
  to { transform: rotate(360deg); }
}
</style>
