<script setup>
import { useConfirm } from '@/composables/useConfirm'

const { confirmState, handleConfirm, handleCancel } = useConfirm()
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="confirmState.visible" class="confirm-overlay" @click.self="handleCancel">
        <div class="confirm-modal" role="dialog" aria-modal="true">
          <h3 class="confirm-title">{{ confirmState.title }}</h3>
          <p class="confirm-message">{{ confirmState.message }}</p>
          <div class="confirm-actions">
            <button type="button" class="btn-cancel" @click="handleCancel">
              {{ confirmState.cancelText }}
            </button>
            <button
              type="button"
              class="btn-confirm"
              :class="confirmState.confirmStyle"
              @click="handleConfirm"
            >
              {{ confirmState.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.confirm-modal {
  background: var(--bg-card, #fff);
  border-radius: var(--radius-lg, 12px);
  padding: var(--space-5, 24px);
  max-width: 400px;
  width: 90%;
  box-shadow: var(--shadow-lg, 0 10px 40px rgba(0,0,0,0.2));
}

.confirm-title {
  margin: 0 0 var(--space-2, 8px);
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.confirm-message {
  margin: 0 0 var(--space-4, 16px);
  font-size: 14px;
  color: var(--text-secondary, #666);
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  gap: var(--space-3, 12px);
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: var(--radius-md, 8px);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel {
  background: var(--bg-subtle, #f5f5f5);
  border: 1px solid var(--border-default, #e0e0e0);
  color: var(--text-secondary, #666);
}

.btn-cancel:hover {
  background: var(--bg-hover, #eee);
}

.btn-confirm {
  border: none;
  color: white;
}

.btn-confirm.danger {
  background: var(--error, #ef4444);
}

.btn-confirm.danger:hover {
  background: #dc2626;
}

.btn-confirm.warning {
  background: var(--warning, #f59e0b);
}

.btn-confirm.warning:hover {
  background: #d97706;
}

.btn-confirm.primary {
  background: var(--primary, #0f9f89);
}

.btn-confirm.primary:hover {
  background: #0d8a77;
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .confirm-modal,
.modal-leave-active .confirm-modal {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.95);
}
</style>
