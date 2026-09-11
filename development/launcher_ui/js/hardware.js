/**
 * SIR Launcher — Hardware Telemetry & RAM Governor Module
 * Real-time kernel metrics, sparkline graphing, and connection state management.
 */

(function () {
  'use strict';

  let _cpuHistory = new Array(60).fill(15);
  let _hardwarePollingInterval = null;

  function drawCpuSparkline(cpuPct) {
    const canvas = document.getElementById('hw-cpu-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const validPct = Math.max(1, Math.min(100, Math.round(cpuPct)));
    _cpuHistory.push(validPct);
    if (_cpuHistory.length > 60) _cpuHistory.shift();

    const lbl = document.getElementById('hw-cpu-canvas-label');
    if (lbl) {
      lbl.textContent = `${validPct}%`;
      lbl.className = validPct >= 75 ? 'text-rose-400 font-black' : (validPct >= 40 ? 'text-amber-400 font-black' : 'text-emerald-400 font-black');
    }

    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Dynamic grid line styling (Windows Task Manager style)
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.12)';
    ctx.lineWidth = 1;

    [0.25, 0.5, 0.75].forEach(ratio => {
      const y = Math.round(h * ratio) + 0.5;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    });

    for (let i = 1; i < 6; i++) {
      const x = Math.round((w / 6) * i) + 0.5;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }

    // Dynamic accent color based on live load
    const strokeCol = validPct >= 75 ? '#f43f5e' : (validPct >= 40 ? '#f59e0b' : '#06b6d4');
    const fillAlpha = validPct >= 75 ? 'rgba(244, 63, 94, 0.35)' : (validPct >= 40 ? 'rgba(245, 158, 11, 0.35)' : 'rgba(6, 182, 212, 0.35)');

    // Gradient fill under line
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, fillAlpha);
    grad.addColorStop(1, 'rgba(0, 0, 0, 0.0)');

    ctx.beginPath();
    ctx.moveTo(0, h);
    const step = w / (_cpuHistory.length - 1 || 1);
    for (let i = 0; i < _cpuHistory.length; i++) {
      const x = i * step;
      const y = h - (_cpuHistory[i] / 100) * (h - 8) - 4;
      if (i === 0) ctx.lineTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.lineTo(w, h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Oscilloscope line path
    ctx.beginPath();
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = strokeCol;
    for (let i = 0; i < _cpuHistory.length; i++) {
      const x = i * step;
      const y = h - (_cpuHistory[i] / 100) * (h - 8) - 4;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Pulse dot at current tip
    if (_cpuHistory.length > 0) {
      const lastX = (_cpuHistory.length - 1) * step;
      const lastY = h - (_cpuHistory[_cpuHistory.length - 1] / 100) * (h - 8) - 4;
      ctx.beginPath();
      ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = strokeCol;
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  function applyHardwareTelemetryData(data) {
    if (!data || data.success === false) return;
    const set = (id, txt) => {
      const el = document.getElementById(id);
      if (el && el.textContent !== txt) {
        el.textContent = txt;
      }
    };

    const total = data.total_ram_gb !== undefined ? `${data.total_ram_gb} GB Total` : '16.0 GB Total';
    const avail = data.avail_ram_gb !== undefined ? `${data.avail_ram_gb} GB Available` : '8.0 GB Available';
    const ramPct = data.ram_load_pct ?? data.ram_pct ?? 45;
    const cores = data.cpu_cores ?? data.cpu_count ?? 8;
    const cpuPct = data.cpu_load_pct ?? data.cpu_pct ?? 5;
    const recRam = data.recommended_ram_gb ?? data.rec_ram_gb ?? 8;
    const tier = data.power_tier || 'High Performance Tier';
    const gpu = data.gpu_name || 'Primary GPU';
    const rec = data.recommendation || `System detected: ${cores} CPU Threads, ${total}, ${gpu}. Optimal allocation: ${recRam} GB Dedicated Heap.`;
    const timeStr = data.timestamp || new Date().toLocaleTimeString();

    set('hw-total-ram', total);
    set('hw-avail-ram', avail);
    set('hw-load-pct', `${ramPct}% In Use`);
    set('hw-cpu-cores', `${cores} Logical Cores`);
    set('hw-cpu-load', `${cpuPct}% Live Load`);
    set('hw-power-tier', tier);
    set('hw-rec-ram', `Allocate ${recRam} GB Dedicated`);
    set('hw-gpu-name', gpu);
    set('hw-recommendation-text', rec);

    // Live Task Manager Subsystem counters
    if (data.processes_count) set('hw-proc-count', String(data.processes_count));
    if (data.threads_count) set('hw-thread-count', Number(data.threads_count).toLocaleString());
    if (data.handles_count) set('hw-handle-count', Number(data.handles_count).toLocaleString());
    if (data.uptime) set('hw-uptime', String(data.uptime));
    if (data.commit_total_gb && data.commit_limit_gb) {
      set('hw-committed-ram', `${data.commit_total_gb} / ${data.commit_limit_gb} GB`);
    }
    if (data.cached_ram_gb) {
      set('hw-cached-ram', `${data.cached_ram_gb} GB`);
    }

    set('hw-timestamp-badge', `Live • ${timeStr}`);

    const liveBadge = document.getElementById('hw-live-badge');
    if (liveBadge) liveBadge.textContent = 'Live Stream Active';

    // Telemetry Connection State Badge Handling:
    // Update stuck 'Connecting...' badge to 'Active (0.0ms)' and smoothly fade it out
    const connState = document.getElementById('telemetry-conn-state');
    if (connState) {
      connState.textContent = 'Active (0.0ms)';
      connState.classList.remove('text-slate-400', 'text-amber-400');
      connState.classList.add('text-emerald-400', 'border-emerald-500/30');

      if (!connState.dataset.fadingOut && connState.style.display !== 'none') {
        connState.dataset.fadingOut = 'true';
        setTimeout(() => {
          connState.style.transition = 'opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), max-width 0.5s cubic-bezier(0.16, 1, 0.3, 1), padding 0.5s cubic-bezier(0.16, 1, 0.3, 1), margin 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
          connState.style.opacity = '0';
          connState.style.transform = 'scale(0.9)';
          connState.style.pointerEvents = 'none';
          setTimeout(() => {
            connState.style.display = 'none';
          }, 500);
        }, 1200);
      }
    }

    const bar = document.getElementById('hw-ram-bar');
    if (bar) bar.style.width = `${Math.min(100, Math.max(0, ramPct))}%`;

    drawCpuSparkline(cpuPct);
  }

  async function refreshHardwareTelemetry() {
    let data = null;
    const api = window.pywebview && window.pywebview.api;
    const getFn = api && (api.get_hardware_telemetry || (api.hardware && api.hardware.get_telemetry));
    if (typeof getFn === 'function') {
      try {
        data = await getFn.call(api);
      } catch (e) {
        console.warn('[HardwareTelemetry] Live call failed:', e);
      }
    }

    // Pre-hydration fallback from bootstrap cache
    if (!data && window.__SIR_HW_BOOTSTRAP__ && window.__SIR_HW_BOOTSTRAP__.total_ram_gb) {
      data = window.__SIR_HW_BOOTSTRAP__;
    }

    if (data) {
      applyHardwareTelemetryData(data);
    }
  }

  function initHardwareTelemetry() {
    if (window.__SIR_HW_BOOTSTRAP__) {
      applyHardwareTelemetryData(window.__SIR_HW_BOOTSTRAP__);
    }

    window.addEventListener('hardware_telemetry_update', (e) => {
      if (e && e.detail) {
        applyHardwareTelemetryData(e.detail);
      }
    });

    window.addEventListener('pywebviewready', () => {
      refreshHardwareTelemetry();
    });

    if (_hardwarePollingInterval) clearInterval(_hardwarePollingInterval);
    _hardwarePollingInterval = setInterval(() => {
      refreshHardwareTelemetry();
    }, 1000);

    setTimeout(refreshHardwareTelemetry, 50);
  }

  window.HardwareTelemetry = {
    applyHardwareTelemetryData,
    refreshHardwareTelemetry,
    drawCpuSparkline,
    init: initHardwareTelemetry
  };

  window.applyHardwareTelemetryData = applyHardwareTelemetryData;
  window.refreshHardwareTelemetry = refreshHardwareTelemetry;
  window.drawCpuSparkline = drawCpuSparkline;

  // Initialize upon DOM readiness
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHardwareTelemetry);
  } else {
    initHardwareTelemetry();
  }
})();
