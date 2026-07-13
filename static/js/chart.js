/**
 * Shared Chart.js configuration/helpers for SHMS.
 * Keeping this separate from script.js mirrors the README's stated
 * static/js/chart.js vs script.js split: chart.js owns chart concerns,
 * script.js owns page/data-polling concerns.
 */

const SHMS_CHART_COLORS = {
  vibration: "#3fd9c4",
  strain: "#7aa6ff",
  temperature: "#f2a93b",
  grid: "rgba(255,255,255,0.06)",
  text: "#8695a3",
};

function shmsBaseChartOptions(yLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: {
        labels: { color: SHMS_CHART_COLORS.text, boxWidth: 10, font: { family: "IBM Plex Mono", size: 11 } },
      },
      tooltip: {
        backgroundColor: "#1d2731",
        borderColor: "#2a3742",
        borderWidth: 1,
        titleColor: "#e7ecf0",
        bodyColor: "#e7ecf0",
        bodyFont: { family: "IBM Plex Mono", size: 11 },
        titleFont: { family: "IBM Plex Mono", size: 11 },
      },
    },
    scales: {
      x: {
        grid: { color: SHMS_CHART_COLORS.grid },
        ticks: { color: SHMS_CHART_COLORS.text, font: { family: "IBM Plex Mono", size: 10 }, maxRotation: 0 },
      },
      y: {
        grid: { color: SHMS_CHART_COLORS.grid },
        ticks: { color: SHMS_CHART_COLORS.text, font: { family: "IBM Plex Mono", size: 10 } },
        title: yLabel ? { display: true, text: yLabel, color: SHMS_CHART_COLORS.text } : undefined,
      },
    },
  };
}

function buildSeriesChart(canvasId, labels, series) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Vibration (mm/s)",
          data: series.vibration,
          borderColor: SHMS_CHART_COLORS.vibration,
          backgroundColor: "transparent",
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 2,
          yAxisID: "y",
        },
        {
          label: "Strain (µɛ)",
          data: series.strain,
          borderColor: SHMS_CHART_COLORS.strain,
          backgroundColor: "transparent",
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 2,
          yAxisID: "y1",
          hidden: false,
        },
        {
          label: "Temperature (°C)",
          data: series.temperature,
          borderColor: SHMS_CHART_COLORS.temperature,
          backgroundColor: "transparent",
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 2,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      ...shmsBaseChartOptions(),
      scales: {
        x: {
          grid: { color: SHMS_CHART_COLORS.grid },
          ticks: { color: SHMS_CHART_COLORS.text, font: { family: "IBM Plex Mono", size: 10 }, maxRotation: 0, autoSkip: true, maxTicksLimit: 8 },
        },
        y: {
          position: "left",
          grid: { color: SHMS_CHART_COLORS.grid },
          ticks: { color: SHMS_CHART_COLORS.text, font: { family: "IBM Plex Mono", size: 10 } },
        },
        y1: {
          position: "right",
          grid: { display: false },
          ticks: { color: SHMS_CHART_COLORS.text, font: { family: "IBM Plex Mono", size: 10 } },
        },
      },
    },
  });
}
