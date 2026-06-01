<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()
const dragStartX = ref(0)
const dragToastId = ref(null)
const dragOffset = ref({})

const getIcon = (type) => {
  const icons = {
    success: 'check_circle',
    error: 'error',
    warning: 'warning',
    info: 'info'
  }
  return icons[type] || 'info'
}

const SWIPE_DISMISS_THRESHOLD = 84

function onPointerDown(event, toastId) {
  if (!event.isPrimary) return
  dragStartX.value = event.clientX
  dragToastId.value = toastId
}

function onPointerMove(event, toastId) {
  if (dragToastId.value !== toastId) return
  const delta = event.clientX - dragStartX.value
  dragOffset.value = {
    ...dragOffset.value,
    [toastId]: delta < 0 ? delta : 0,
  }
}

function onPointerRelease(toastId) {
  if (dragToastId.value !== toastId) return
  const delta = Number(dragOffset.value[toastId] || 0)
  const nextOffsets = { ...dragOffset.value }
  delete nextOffsets[toastId]
  dragOffset.value = nextOffsets
  dragToastId.value = null

  if (Math.abs(delta) >= SWIPE_DISMISS_THRESHOLD) {
    remove(toastId)
  }
}

function toastStyle(toastId) {
  const delta = Number(dragOffset.value[toastId] || 0)
  if (!delta) return null
  return {
    transform: `translateX(${delta}px)`,
    opacity: Math.max(0.4, 1 - Math.abs(delta) / 180),
  }
}
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`, { 'toast-exit': !toast.visible }]"
        :style="toastStyle(toast.id)"
        @pointerdown="onPointerDown($event, toast.id)"
        @pointermove="onPointerMove($event, toast.id)"
        @pointerup="onPointerRelease(toast.id)"
        @pointercancel="onPointerRelease(toast.id)"
        @pointerleave="onPointerRelease(toast.id)"
      >
        <span class="material-icons toast-icon">{{ getIcon(toast.type) }}</span>
        <span class="toast-message">{{ toast.message }}</span>
        <div class="toast-actions">
          <button class="toast-dismiss" @click.stop="remove(toast.id)">Dismiss</button>
          <button class="toast-close" @click.stop="remove(toast.id)">
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 320px;
  max-width: 420px;
  padding: 14px 16px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  border-left: 3px solid;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s ease;
  touch-action: pan-y;
}

.toast:hover {
  transform: translateX(-4px);
  box-shadow: var(--shadow-lg);
}

.toast-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}

.toast-actions {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.toast-dismiss {
  border: 1px solid var(--border-default);
  background: transparent;
  color: var(--text-secondary);
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.toast-dismiss:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toast-close {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.toast-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toast-close .material-icons {
  font-size: 18px;
}

.toast-success {
  border-left-color: var(--success);
  background: var(--success-bg);
}

.toast-success .toast-icon {
  color: var(--success);
}

.toast-error {
  border-left-color: var(--error);
  background: var(--error-bg);
}

.toast-error .toast-icon {
  color: var(--error);
}

.toast-warning {
  border-left-color: var(--warning);
  background: var(--warning-bg);
}

.toast-warning .toast-icon {
  color: var(--warning);
}

.toast-info {
  border-left-color: var(--info);
  background: var(--info-bg);
}

.toast-info .toast-icon {
  color: var(--info);
}

/* Animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}

@media (max-width: 600px) {
  .toast-container {
    left: 20px;
    right: 20px;
    top: 70px;
  }

  .toast {
    min-width: auto;
    max-width: none;
  }
}
</style>
