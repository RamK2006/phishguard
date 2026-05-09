/**
 * PhishGuard — URL Scanner Content Script
 *
 * Injects risk overlays based on scan results:
 * - SAFE: green shield badge
 * - SUSPICIOUS: amber warning banner
 * - MALICIOUS: full-page glassmorphic block overlay
 */

// Listen for scan results from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'PHISHGUARD_SCAN_RESULT') {
    const result = message.data;
    removeExistingOverlays();

    switch (result.risk_level) {
      case 'safe':
        injectSafeBadge(result);
        break;
      case 'suspicious':
        injectSuspiciousBanner(result);
        break;
      case 'malicious':
        injectMaliciousOverlay(result);
        break;
    }
  }
});

function removeExistingOverlays(): void {
  document.querySelectorAll('[data-phishguard]').forEach(el => el.remove());
}

function injectSafeBadge(result: any): void {
  const badge = document.createElement('div');
  badge.setAttribute('data-phishguard', 'safe-badge');
  badge.innerHTML = `
    <div style="
      position: fixed; bottom: 20px; right: 20px; z-index: 2147483647;
      background: rgba(34, 197, 94, 0.15);
      backdrop-filter: blur(16px) saturate(180%);
      border: 1px solid rgba(34, 197, 94, 0.3);
      border-radius: 12px; padding: 10px 16px;
      display: flex; align-items: center; gap: 8px;
      font-family: 'Inter', -apple-system, sans-serif;
      color: #22C55E; font-size: 13px; font-weight: 600;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      animation: phishguard-slide-in 0.35s ease-out;
      cursor: pointer;
    " onclick="this.parentElement.remove()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        <path d="m9 12 2 2 4-4"/>
      </svg>
      <span>PhishGuard: Safe</span>
      <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; opacity: 0.8;">
        ${(result.risk_score * 100).toFixed(0)}%
      </span>
    </div>
  `;

  const style = document.createElement('style');
  style.setAttribute('data-phishguard', 'styles');
  style.textContent = `
    @keyframes phishguard-slide-in {
      from { transform: translateX(100px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;

  document.body.appendChild(style);
  document.body.appendChild(badge);

  // Auto-dismiss after 5 seconds
  setTimeout(() => badge.remove(), 5000);
}

function injectSuspiciousBanner(result: any): void {
  const banner = document.createElement('div');
  banner.setAttribute('data-phishguard', 'suspicious-banner');
  banner.innerHTML = `
    <div style="
      position: fixed; top: 0; left: 0; right: 0; z-index: 2147483647;
      background: rgba(245, 158, 11, 0.12);
      backdrop-filter: blur(16px) saturate(180%);
      border-bottom: 1px solid rgba(245, 158, 11, 0.3);
      padding: 12px 20px;
      display: flex; align-items: center; justify-content: space-between;
      font-family: 'Inter', -apple-system, sans-serif;
      color: #F59E0B;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      animation: phishguard-slide-down 0.35s ease-out;
    ">
      <div style="display: flex; align-items: center; gap: 12px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <path d="M12 9v4M12 17h.01"/>
        </svg>
        <span style="font-weight: 600; font-size: 14px;">
          ⚠ PhishGuard Warning — This page may be suspicious
        </span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; opacity: 0.8;">
          Risk: ${(result.risk_score * 100).toFixed(1)}%
        </span>
      </div>
      <button style="
        background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 6px; padding: 6px 14px; color: #F59E0B;
        cursor: pointer; font-size: 12px; font-weight: 600;
      " onclick="this.closest('[data-phishguard]').remove()">
        Dismiss
      </button>
    </div>
  `;

  const style = document.createElement('style');
  style.setAttribute('data-phishguard', 'styles');
  style.textContent = `
    @keyframes phishguard-slide-down {
      from { transform: translateY(-100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `;

  document.body.appendChild(style);
  document.body.appendChild(banner);
}

function injectMaliciousOverlay(result: any): void {
  const overlay = document.createElement('div');
  overlay.setAttribute('data-phishguard', 'malicious-overlay');

  const riskFactors = (result.explanation?.risk_factors || [])
    .map((f: string) => `<li style="padding: 4px 0;">${f}</li>`)
    .join('');

  overlay.innerHTML = `
    <div style="
      position: fixed; inset: 0; z-index: 2147483647;
      background: rgba(10, 14, 26, 0.92);
      backdrop-filter: blur(20px) saturate(180%);
      display: flex; align-items: center; justify-content: center;
      font-family: 'Inter', -apple-system, sans-serif;
      animation: phishguard-fade-in 0.35s ease-out;
    ">
      <div style="
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 24px; padding: 48px;
        max-width: 540px; width: 90%;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
        animation: phishguard-scale-in 0.35s ease-out;
        text-align: center;
      ">
        <div style="
          width: 64px; height: 64px; margin: 0 auto 20px;
          background: rgba(239, 68, 68, 0.15); border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
        ">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M12 8v4M12 16h.01"/>
          </svg>
        </div>

        <h2 style="color: #EF4444; font-size: 24px; font-weight: 700; margin: 0 0 8px;">
          🛡 Phishing Detected
        </h2>
        <p style="color: #94A3B8; font-size: 14px; margin: 0 0 20px;">
          PhishGuard has blocked this page for your protection.
        </p>

        <div style="
          background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 12px; padding: 16px; margin-bottom: 20px; text-align: left;
        ">
          <div style="color: #EF4444; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
            Risk Score
          </div>
          <div style="font-family: 'JetBrains Mono', monospace; color: #EF4444; font-size: 32px; font-weight: 700;">
            ${(result.risk_score * 100).toFixed(1)}%
          </div>
        </div>

        ${riskFactors ? `
        <div style="text-align: left; margin-bottom: 24px;">
          <div style="color: #94A3B8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
            Risk Factors
          </div>
          <ul style="color: #CBD5E1; font-size: 13px; list-style: none; padding: 0; margin: 0;">
            ${riskFactors}
          </ul>
        </div>
        ` : ''}

        <div style="display: flex; gap: 12px; justify-content: center;">
          <button onclick="history.back()" style="
            background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 8px; padding: 10px 24px; color: #3B82F6;
            cursor: pointer; font-size: 14px; font-weight: 600;
            transition: all 0.15s;
          " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            ← Go Back (Safe)
          </button>
          <button onclick="this.closest('[data-phishguard]').remove()" style="
            background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px; padding: 10px 24px; color: #94A3B8;
            cursor: pointer; font-size: 14px; font-weight: 500;
            transition: all 0.15s;
          ">
            Proceed Anyway
          </button>
        </div>
      </div>
    </div>
  `;

  const style = document.createElement('style');
  style.setAttribute('data-phishguard', 'styles');
  style.textContent = `
    @keyframes phishguard-fade-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes phishguard-scale-in {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `;

  document.body.appendChild(style);
  document.body.appendChild(overlay);
}

export {};
