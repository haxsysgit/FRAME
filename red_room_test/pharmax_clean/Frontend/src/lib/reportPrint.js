function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderHighlights(highlights) {
  if (!Array.isArray(highlights) || highlights.length === 0) return ''

  return `
    <section class="meta-grid">
      ${highlights
        .map(
          (item) => `
            <article class="meta-card">
              <h4>${escapeHtml(item?.label || '')}</h4>
              <p>${escapeHtml(item?.value ?? '')}</p>
            </article>
          `,
        )
        .join('')}
    </section>
  `
}

function renderTable(table) {
  const columns = Array.isArray(table?.columns) ? table.columns : []
  const rows = Array.isArray(table?.rows) ? table.rows : []

  return `
    <section class="table-section">
      <h3>${escapeHtml(table?.title || '')}</h3>
      ${rows.length > 0
        ? `
        <table>
          <thead>
            <tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${rows
              .map(
                (row) => `
                  <tr>
                    ${columns
                      .map((_, index) => `<td>${escapeHtml(row?.[index] ?? '-')}</td>`)
                      .join('')}
                  </tr>
                `,
              )
              .join('')}
          </tbody>
        </table>
      `
        : `<p class="empty">${escapeHtml(table?.emptyMessage || 'No rows available for this section.')}</p>`}
    </section>
  `
}

export function printStructuredReport({
  title,
  subtitle,
  reportDateLabel,
  periodLabel,
  generatedBy,
  highlights = [],
  tables = [],
}) {
  if (typeof window === 'undefined') return false

  const printWindow = window.open('', '_blank', 'width=1100,height=800')
  if (!printWindow) return false

  const generatedAt = new Date()
  const metaRows = [
    ['Printed at', generatedAt.toLocaleString()],
    ['Printed by', generatedBy || 'Unknown user'],
  ]

  if (reportDateLabel) {
    metaRows.push(['Report date', reportDateLabel])
  }
  if (periodLabel) {
    metaRows.push(['Period', periodLabel])
  }

  const html = `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(title || 'Report')}</title>
        <style>
          * { box-sizing: border-box; }
          body {
            margin: 0;
            padding: 28px;
            font-family: Arial, sans-serif;
            color: #0f172a;
            background: #fff;
          }
          .header {
            border-bottom: 2px solid #0f172a;
            padding-bottom: 14px;
            margin-bottom: 18px;
          }
          .header h1 {
            margin: 0;
            font-size: 24px;
          }
          .header p {
            margin: 6px 0 0;
            color: #475569;
            font-size: 13px;
          }
          .meta-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 18px;
          }
          .meta-table td {
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
            font-size: 12px;
          }
          .meta-table td:first-child {
            width: 140px;
            font-weight: 700;
            background: #f8fafc;
          }
          .meta-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 16px;
          }
          .meta-card {
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 10px;
            background: #f8fafc;
          }
          .meta-card h4 {
            margin: 0;
            font-size: 12px;
            color: #475569;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }
          .meta-card p {
            margin: 8px 0 0;
            font-size: 16px;
            font-weight: 700;
          }
          .table-section {
            margin-top: 14px;
            break-inside: avoid;
          }
          .table-section h3 {
            margin: 0 0 8px;
            font-size: 16px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #cbd5e1;
          }
          th, td {
            border: 1px solid #cbd5e1;
            padding: 8px;
            text-align: left;
            font-size: 12px;
          }
          th {
            background: #e2e8f0;
            font-weight: 700;
          }
          .empty {
            margin: 0;
            padding: 10px;
            border: 1px dashed #94a3b8;
            color: #475569;
            font-size: 12px;
          }
          @page { size: A4 portrait; margin: 14mm; }
        </style>
      </head>
      <body>
        <header class="header">
          <h1>${escapeHtml(title || 'Report')}</h1>
          ${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ''}
        </header>

        <table class="meta-table">
          <tbody>
            ${metaRows
              .map(
                ([key, value]) => `
                  <tr>
                    <td>${escapeHtml(key)}</td>
                    <td>${escapeHtml(value)}</td>
                  </tr>
                `,
              )
              .join('')}
          </tbody>
        </table>

        ${renderHighlights(highlights)}
        ${tables.map((table) => renderTable(table)).join('')}
      </body>
    </html>
  `

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
  printWindow.focus()

  window.setTimeout(() => {
    printWindow.print()
  }, 400)

  return true
}
