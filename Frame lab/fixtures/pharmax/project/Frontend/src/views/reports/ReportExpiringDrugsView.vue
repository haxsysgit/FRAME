<script setup>
import { useAuthStore } from '@/stores/auth'
import { printStructuredReport } from '@/lib/reportPrint'

const auth = useAuthStore()

const statusSummary =
  'Expiry Watch is in manual mode. Backend report data does not include batch numbers or expiry dates yet, so automated alerts are still unavailable.'

const missingBackendData = [
  'Current /dashboard/reports data includes low-stock rows only.',
  'No batch_no, expiry_date, or days_left fields are returned.',
  'No dedicated /dashboard/reports/expiring endpoint is available.',
]

const interimWorkflow = [
  {
    title: 'Monitor near-term risk using Low Stock Watchlist',
    detail: 'Use reorder-level alerts to catch products likely to run out before expiry tracking is available.',
    route: '/stock/low-stock',
  },
  {
    title: 'Handle urgent gaps from Out-of-Stock Items',
    detail: 'Prioritize immediate replenishment to reduce missed sales until expiry tracking is ready.',
    route: '/stock/out-of-stock',
  },
  {
    title: 'Track batch expiry manually at receiving',
    detail: 'Record batch number, quantity, and expiry date in your procurement log until backend support is added.',
    route: null,
  },
]

const activationRequirements = [
  'Add batch-level inventory data with product_id, batch_no, expiry_date, and quantity_on_hand.',
  'Capture and persist expiry data during stock intake, adjustments, and sales consumption.',
  'Add GET /dashboard/reports/expiring endpoint with grouped counts and row-level results.',
  'Return risk buckets (expired, ≤30 days, 31–60 days, 61–90 days) plus days_left for sorting and alerts.',
  'Enable CSV export with live expiry rows after endpoint contract is connected.',
]

function printReport() {
  printStructuredReport({
    title: 'Expiry Watch (Manual Mode)',
    subtitle: 'Backend expiry data is not available yet. This printout shows the interim operating guide.',
    generatedBy: auth.user?.full_name || auth.user?.username,
    highlights: [
      { label: 'Current mode', value: 'Manual' },
      { label: 'Missing backend items', value: String(missingBackendData.length) },
      { label: 'Activation checklist items', value: String(activationRequirements.length) },
    ],
    tables: [
      {
        title: 'Missing backend data',
        columns: ['Item'],
        rows: missingBackendData.map((item) => [item]),
      },
      {
        title: 'Interim workflow',
        columns: ['Step', 'Details'],
        rows: interimWorkflow.map((step) => [step.title, step.detail]),
      },
      {
        title: 'Activation checklist',
        columns: ['Required item'],
        rows: activationRequirements.map((item) => [item]),
      },
    ],
  })
}
</script>

<template>
  <section class="report-page">
    <header class="report-header">
      <div class="title-wrap">
        <h2>Expiry Watch</h2>
        <p>Manual workflow while backend expiry data is unavailable.</p>
      </div>

      <div class="report-actions">
        <label class="filter-field">
          <span>Expiry window</span>
          <select class="filter-select" disabled>
            <option>Next 30 days</option>
            <option>Next 60 days</option>
            <option>Next 90 days</option>
          </select>
        </label>
        <button type="button" class="btn btn-primary" disabled>Export CSV</button>
        <button type="button" class="btn btn-secondary" @click="printReport">Print</button>
      </div>
      <p class="action-note">
        Filter and CSV export will unlock after all activation checklist items are complete.
      </p>
    </header>

    <article class="report-card status-card">
      <h3>Current status: Manual mode</h3>
      <p>{{ statusSummary }}</p>
    </article>

    <div class="card-grid">
      <article class="report-card">
        <h3>Missing backend data right now</h3>
        <ul class="stack-list">
          <li v-for="item in missingBackendData" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article class="report-card">
        <h3>Interim workflow you can use today</h3>
        <ol class="stack-list">
          <li v-for="step in interimWorkflow" :key="step.title">
            <p class="item-title">{{ step.title }}</p>
            <p>{{ step.detail }}</p>
            <RouterLink v-if="step.route" :to="step.route" class="inline-link">Open report</RouterLink>
          </li>
        </ol>
      </article>
    </div>

    <article class="report-card">
      <h3>What Expiry Watch will show after activation</h3>
      <ul class="stack-list">
        <li>Header actions: expiry-window filter + export/print controls.</li>
        <li>Top KPI cards: expired, due ≤30 days, due 31–60 days, due 61–90 days.</li>
        <li>Main table: product, batch no, quantity, expiry date, days left, risk level.</li>
        <li>Action panel: urgent disposal, markdown candidates, and reorder suggestions.</li>
      </ul>
    </article>

    <article class="report-card">
      <h3>Activation checklist</h3>
      <p class="support-note">All items below are required before this page can move out of manual mode.</p>
      <ol class="stack-list">
        <li v-for="item in activationRequirements" :key="item">{{ item }}</li>
      </ol>
    </article>
  </section>
</template>

<style scoped>
.report-page {
  display: grid;
  gap: var(--space-4);
}

.report-header,
.report-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

.report-header {
  padding: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.title-wrap {
  display: grid;
  gap: 4px;
}

.title-wrap h2 {
  margin: 0;
  font-size: 24px;
}

.title-wrap p {
  margin: 0;
  color: var(--text-secondary);
}

.report-actions {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.action-note {
  margin: 0;
  width: 100%;
  font-size: 12px;
  color: var(--text-muted);
}

.filter-field {
  display: grid;
  gap: 6px;
  min-width: 210px;
}

.filter-field span {
  font-size: 12px;
  color: var(--text-muted);
}

.filter-select {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 0 12px;
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.btn {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
}

.btn-secondary {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.btn:disabled,
.filter-select:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.card-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.report-card {
  padding: var(--space-4);
  display: grid;
  gap: var(--space-2);
}

.status-card {
  border-color: var(--warning-tint);
  background: var(--warning-bg);
}

.report-card h3 {
  margin: 0;
  font-size: 18px;
}

.report-card p,
.report-card ul,
.report-card ol {
  margin: 0;
  color: var(--text-secondary);
}

.support-note {
  margin: 0;
  color: var(--text-muted) !important;
  font-size: 12px;
}

.stack-list {
  padding-left: 18px;
  display: grid;
  gap: 8px;
}

.item-title {
  font-weight: 600;
  color: var(--text-primary) !important;
}

.inline-link {
  margin-top: 4px;
  display: inline-flex;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.inline-link:hover {
  text-decoration: underline;
}

@media (max-width: 980px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .report-header {
    align-items: stretch;
  }

  .report-actions,
  .filter-field {
    width: 100%;
  }
}

@media print {
  .report-actions,
  .inline-link {
    display: none;
  }

  .report-header,
  .report-card {
    box-shadow: none;
  }
}
</style>
