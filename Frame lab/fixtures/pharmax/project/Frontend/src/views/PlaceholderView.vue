<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isTeamAccessPage = computed(() => route.name === 'users')
</script>

<template>
  <section class="placeholder">
    <article class="card">
      <p class="label">{{ route.meta?.label }}</p>
      <h2>{{ isTeamAccessPage ? 'Team & Access Workspace' : 'Screen Skeleton Ready' }}</h2>
      <p v-if="isTeamAccessPage">
        This page is reserved for admin staff management: create staff/cashier accounts, reset PIN/password,
        and control role permissions.
      </p>
      <p v-else>
        Shared layout, navigation, and theme toggle are active. This page is wired and ready for API
        integration.
      </p>
    </article>
  </section>
</template>

<style scoped>
.placeholder {
  min-height: 100%;
}

.card {
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 24px;
  background: var(--bg-card);
  max-width: 780px;
}

.label {
  margin: 0;
  color: var(--accent);
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

h2 {
  margin: 8px 0 0;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 36px;
  line-height: 1;
}

p {
  margin: 12px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
  max-width: 560px;
}
</style>
