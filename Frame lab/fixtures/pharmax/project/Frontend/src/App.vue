<script setup>
import ToastNotification from '@/components/ToastNotification.vue'
import GlobalLoadingOverlay from '@/components/GlobalLoadingOverlay.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
</script>

<template>
  <RouterView />
  <GlobalLoadingOverlay />
  <ToastNotification />
  <ConfirmModal />
</template>
