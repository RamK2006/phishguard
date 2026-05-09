/**
 * PhishGuard — Popup Script
 *
 * Animated arc gauge for current page risk, last 5 scans, pause toggle.
 */

const gaugeContainer = document.getElementById('gaugeContainer')!;
const scanList = document.getElementById('scanList')!;
const scanToggle = document.getElementById('scanToggle')!;

// ─── Risk Gauge SVG ───
function renderGauge(score: number, riskLevel: string): void {
  const percentage = Math.round(score * 100);
  const color = riskLevel === 'malicious' ? '#EF4444' :
                riskLevel === 'suspicious' ? '#F59E0B' : '#22C55E';

  // Arc: 180 degrees, radius 70, cx=90, cy=85
  const radius = 70;
  const circumference = Math.PI * radius;
  const dashOffset = circumference - (score * circumference);

  gaugeContainer.innerHTML = `
    <svg class="gauge-svg" viewBox="0 0 180 110">
      <path d="M 10 90 A 70 70 0 0 1 170 90"
            fill="none" stroke="#1E293B" stroke-width="12" stroke-linecap="round"/>
      <path d="M 10 90 A 70 70 0 0 1 170 90"
            fill="none" stroke="${color}" stroke-width="12" stroke-linecap="round"
            stroke-dasharray="${circumference}"
            stroke-dashoffset="${dashOffset}"
            style="transition: stroke-dashoffset 1.5s ease-in-out;"/>
    </svg>
    <div class="gauge-label">Current Page Risk</div>
    <div class="gauge-score" style="color: ${color}">${percentage}%</div>
    <div class="risk-badge risk-${riskLevel}">${riskLevel.toUpperCase()}</div>
  `;
}

// ─── Recent Scans List ───
function renderScans(scans: any[]): void {
  if (scans.length === 0) {
    scanList.innerHTML = '<div class="empty-state">No recent scans</div>';
    return;
  }

  scanList.innerHTML = scans.slice(0, 5).map(scan => {
    const color = scan.risk_level === 'malicious' ? '#EF4444' :
                  scan.risk_level === 'suspicious' ? '#F59E0B' : '#22C55E';
    const url = scan.url || '';
    const shortUrl = url.length > 45 ? url.substring(0, 45) + '...' : url;
    const time = scan.timestamp ? new Date(scan.timestamp).toLocaleTimeString() : '';

    return `
      <div class="scan-item">
        <div class="scan-url">${shortUrl}</div>
        <div class="scan-meta">
          <span class="scan-score" style="color: ${color}">
            ${(scan.risk_score * 100).toFixed(1)}% — ${scan.risk_level}
          </span>
          <span class="scan-time">${time}</span>
        </div>
      </div>
    `;
  }).join('');
}

// ─── Toggle ───
scanToggle.addEventListener('click', async () => {
  const { scanPaused } = await chrome.storage.sync.get('scanPaused');
  const newState = !scanPaused;
  await chrome.storage.sync.set({ scanPaused: newState });
  scanToggle.classList.toggle('active', !newState);
  (scanToggle.nextElementSibling as HTMLElement).textContent =
    newState ? 'Protection Paused' : 'Protection Active';
});

// ─── Initialize ───
async function init(): Promise<void> {
  // Load toggle state
  const { scanPaused } = await chrome.storage.sync.get('scanPaused');
  scanToggle.classList.toggle('active', !scanPaused);
  (scanToggle.nextElementSibling as HTMLElement).textContent =
    scanPaused ? 'Protection Paused' : 'Protection Active';

  // Scan current tab
  try {
    chrome.runtime.sendMessage({ type: 'SCAN_CURRENT_TAB' }, (result) => {
      if (result) {
        renderGauge(result.risk_score, result.risk_level);
      } else {
        renderGauge(0, 'safe');
      }
    });
  } catch {
    renderGauge(0, 'safe');
  }

  // Load recent scans
  chrome.runtime.sendMessage({ type: 'GET_RECENT_SCANS' }, (scans) => {
    renderScans(scans || []);
  });
}

init();
