/**
 * History page logic: paginated log table + full trend chart.
 */

(function () {
  let currentPage = 1;
  let historyChart = null;

  async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }

  function formatTimestamp(ts) {
    const d = new Date(ts.replace(" ", "T") + "Z");
    if (isNaN(d.getTime())) return ts;
    return d.toLocaleString([], {
      month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  }

  function renderTable(rows) {
    const tbody = document.getElementById("history-tbody");
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-row">No readings recorded yet. Visit the Live page to start the feed.</td></tr>';
      return;
    }
    tbody.innerHTML = rows.map((r) => `
      <tr>
        <td>${formatTimestamp(r.created_at)}</td>
        <td>${Number(r.vibration).toFixed(2)}</td>
        <td>${Number(r.strain).toFixed(1)}</td>
        <td>${Number(r.temperature).toFixed(1)}</td>
        <td><span class="status-chip ${r.status === "Healthy" ? "healthy" : "damaged"}">${r.status}</span></td>
        <td>${r.confidence != null ? Math.round(r.confidence * 100) + "%" : "—"}</td>
      </tr>
    `).join("");
  }

  async function loadPage(page) {
    const data = await fetchJSON(`/api/history?page=${page}`);
    currentPage = data.page;

    renderTable(data.data);

    document.getElementById("history-count").textContent = `${data.total} total readings`;
    document.getElementById("page-indicator").textContent = `Page ${data.page} of ${data.total_pages}`;
    document.getElementById("prev-page").disabled = data.page <= 1;
    document.getElementById("next-page").disabled = data.page >= data.total_pages;
  }

  async function loadChart() {
    const rows = await fetchJSON("/api/history/series?limit=100");
    const labels = rows.map((r) => formatTimestamp(r.created_at));
    const series = {
      vibration: rows.map((r) => r.vibration),
      strain: rows.map((r) => r.strain),
      temperature: rows.map((r) => r.temperature),
    };

    if (rows.length) {
      document.getElementById("history-range").textContent =
        `${formatTimestamp(rows[0].created_at)} — ${formatTimestamp(rows[rows.length - 1].created_at)}`;
    }

    historyChart = buildSeriesChart("history-chart", labels, series);
  }

  document.addEventListener("DOMContentLoaded", () => {
    loadPage(1);
    loadChart();

    document.getElementById("prev-page").addEventListener("click", () => {
      if (currentPage > 1) loadPage(currentPage - 1);
    });
    document.getElementById("next-page").addEventListener("click", () => {
      loadPage(currentPage + 1);
    });
  });
})();
