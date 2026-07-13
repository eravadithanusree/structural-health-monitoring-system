/**
 * Live dashboard logic: polls the simulated sensor feed and updates
 * the DOM + trend chart + status hero without a page reload.
 */

(function () {
  const POLL_MS = 3000;
  const THRESHOLDS = window.SHMS_THRESHOLDS || {
    vibration: { warning: 4.0, critical: 6.0 },
    strain: { warning: 180, critical: 250 },
    temperature: { warning: 45, critical: 60 },
  };

  let trendChart = null;
  let failureStreak = 0;

  function setConnPill(isUp) {
    const pill = document.getElementById("conn-pill");
    if (!pill) return;
    pill.classList.toggle("is-down", !isUp);
    pill.innerHTML = isUp
      ? '<span class="live-dot"></span> Live'
      : '<span class="live-dot"></span> Reconnecting';
  }

  function levelFor(metric, value) {
    const t = THRESHOLDS[metric];
    if (!t) return "normal";
    if (value >= t.critical) return "critical";
    if (value >= t.warning) return "warning";
    return "normal";
  }

  function updateReadoutCard(metric, value) {
    const valueEl = document.getElementById(`value-${metric}`);
    const barEl = document.getElementById(`bar-${metric}`);
    const cardEl = document.querySelector(`.readout-card[data-metric="${metric}"]`);
    if (!valueEl || !barEl || !cardEl) return;

    const decimals = metric === "strain" ? 1 : metric === "temperature" ? 1 : 2;
    valueEl.textContent = Number(value).toFixed(decimals);

    const t = THRESHOLDS[metric];
    const scaleMax = t.critical * 1.3;
    const pct = Math.min((value / scaleMax) * 100, 100);
    barEl.style.width = `${pct}%`;

    const level = levelFor(metric, value);
    cardEl.classList.toggle("is-warning", level === "warning");
    cardEl.classList.toggle("is-critical", level === "critical");
  }

  function updateStatusHero(status, confidence, timestamp) {
    const hero = document.getElementById("status-hero");
    const title = document.getElementById("status-title");
    const confEl = document.getElementById("status-confidence");
    const tsEl = document.getElementById("status-timestamp");

    const state = status === "Healthy" ? "healthy" : "damaged";
    hero.dataset.state = state;
    title.textContent = status;
    confEl.textContent = confidence != null ? `${Math.round(confidence * 100)}%` : "—";
    tsEl.textContent = timestamp ? formatTimestamp(timestamp) : "—";
  }

  function formatTimestamp(ts) {
    // SQLite datetime('now') is UTC 'YYYY-MM-DD HH:MM:SS'
    const d = new Date(ts.replace(" ", "T") + "Z");
    if (isNaN(d.getTime())) return ts;
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }

  async function refreshSeries() {
    const rows = await fetchJSON("/api/history/series?limit=30");
    if (!rows.length) return;

    const labels = rows.map((r) => formatTimestamp(r.created_at));
    const series = {
      vibration: rows.map((r) => r.vibration),
      strain: rows.map((r) => r.strain),
      temperature: rows.map((r) => r.temperature),
    };

    if (!trendChart) {
      trendChart = buildSeriesChart("trend-chart", labels, series);
    } else {
      trendChart.data.labels = labels;
      trendChart.data.datasets[0].data = series.vibration;
      trendChart.data.datasets[1].data = series.strain;
      trendChart.data.datasets[2].data = series.temperature;
      trendChart.update("none");
    }
  }

  async function pollOnce() {
    try {
      // Generate one simulated reading (server-side) then read back latest state.
      const reading = await fetchJSON("/api/simulate/tick", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ structure_id: "default" }),
      });

      updateReadoutCard("vibration", reading.vibration);
      updateReadoutCard("strain", reading.strain);
      updateReadoutCard("temperature", reading.temperature);
      updateStatusHero(reading.status, reading.confidence, new Date().toISOString().replace("T", " ").slice(0, 19));

      await refreshSeries();

      failureStreak = 0;
      setConnPill(true);
    } catch (err) {
      failureStreak += 1;
      setConnPill(false);
      console.error("SHMS poll failed:", err);
    }
  }

  function updateFooterClock() {
    const el = document.getElementById("footer-clock");
    if (el) el.textContent = new Date().toLocaleString();
  }

  function initPredictForm() {
    const form = document.getElementById("predict-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        vibration: parseFloat(document.getElementById("input-vibration").value),
        strain: parseFloat(document.getElementById("input-strain").value),
        temperature: parseFloat(document.getElementById("input-temperature").value),
      };

      try {
        const result = await fetchJSON("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const resultWrap = document.getElementById("predict-result");
        const badge = document.getElementById("predict-badge");
        const confText = document.getElementById("predict-confidence-text");

        resultWrap.hidden = false;
        badge.textContent = result.status;
        badge.className = `predict-badge ${result.status === "Healthy" ? "healthy" : "damaged"}`;
        confText.textContent = `Model confidence: ${Math.round(result.confidence * 100)}%`;
      } catch (err) {
        console.error("Predict failed:", err);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initPredictForm();
    updateFooterClock();
    setInterval(updateFooterClock, 1000);

    pollOnce();
    setInterval(pollOnce, POLL_MS);
  });
})();
