function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export function thermalEscape(value) {
  return escapeHtml(value)
}

export function printThermalDocument({ title = '', bodyHtml = '', printWindow: providedWindow = null } = {}) {
  if (typeof window === 'undefined') return false

  const printWindow = providedWindow || window.open('', '_blank', 'noopener,noreferrer,width=420,height=760')
  if (!printWindow || printWindow.closed) return false

  const html = `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(title)}</title>
        <style>
          * { box-sizing: border-box; }
          @page { size: 80mm auto; margin: 2.5mm; }
          html, body { width: 80mm; margin: 0; padding: 0; background: #fff; }
          body {
            font-family: Arial, sans-serif;
            color: #0f172a;
            font-size: 12px;
            line-height: 1.35;
          }
          .slip {
            width: 100%;
            padding: 1mm 0;
          }
          .center { text-align: center; }
          .title {
            font-size: 16px;
            font-weight: 700;
            margin: 0;
          }
          .muted {
            color: #475569;
            font-size: 11px;
            margin: 2px 0 0;
          }
          .divider {
            border-top: 1px dashed #94a3b8;
            margin: 8px 0;
          }
          .line {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            padding: 2px 0;
          }
          .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
          .strong { font-weight: 700; }
          .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 4px;
            font-size: 11px;
          }
          .table th,
          .table td {
            text-align: left;
            padding: 3px 2px;
            border-bottom: 1px dashed #cbd5e1;
            vertical-align: top;
          }
          .table th:last-child,
          .table td:last-child {
            text-align: right;
          }
          .table th:nth-child(2),
          .table td:nth-child(2) {
            text-align: center;
            width: 14%;
          }
          .table th:nth-child(3),
          .table td:nth-child(3),
          .table th:nth-child(4),
          .table td:nth-child(4) {
            width: 23%;
          }
          .grand {
            border-top: 1px solid #0f172a;
            margin-top: 6px;
            padding-top: 4px;
            font-size: 14px;
            font-weight: 700;
          }
          .footer {
            text-align: center;
            margin-top: 8px;
            font-size: 11px;
            color: #475569;
          }
          .uppercase {
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 10px;
            color: #64748b;
          }
        </style>
      </head>
      <body>
        <main class="slip">
          ${bodyHtml}
        </main>
      </body>
    </html>
  `

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
  printWindow.focus()

  window.setTimeout(() => {
    printWindow.print()
    printWindow.close()
  }, 180)

  return true
}
