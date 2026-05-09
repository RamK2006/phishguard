/**
 * PhishGuard — Email Scanner Content Script
 *
 * Injects into Gmail and Outlook, extracts links + headers,
 * calls /scan/email, injects risk sidebar.
 */

const API_BASE = 'http://localhost:8000';
const EXTENSION_KEY = 'phishguard-extension-dev';

// Gmail-specific selectors
const GMAIL_EMAIL_BODY = '.a3s.aiL';
const GMAIL_SUBJECT = '.hP';
const GMAIL_SENDER = '.gD';

// Outlook-specific selectors
const OUTLOOK_EMAIL_BODY = '[role="document"]';

function isGmail(): boolean {
  return window.location.hostname === 'mail.google.com';
}

function isOutlook(): boolean {
  return window.location.hostname.includes('outlook');
}

function extractLinks(): string[] {
  const selector = isGmail() ? GMAIL_EMAIL_BODY : OUTLOOK_EMAIL_BODY;
  const container = document.querySelector(selector);
  if (!container) return [];

  const anchors = container.querySelectorAll('a[href]');
  const links: string[] = [];
  anchors.forEach(a => {
    const href = a.getAttribute('href');
    if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
      links.push(href);
    }
  });
  return [...new Set(links)];
}

function extractSender(): string {
  if (isGmail()) {
    const el = document.querySelector(GMAIL_SENDER);
    return el?.getAttribute('email') || el?.textContent || '';
  }
  return '';
}

async function scanEmailLinks(): Promise<void> {
  const links = extractLinks();
  if (links.length === 0) return;

  try {
    const resp = await fetch(`${API_BASE}/api/v1/scan/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Extension-Key': EXTENSION_KEY,
      },
      body: JSON.stringify({
        sender: extractSender(),
        links,
        headers: {},
      }),
    });

    if (resp.ok) {
      const data = await resp.json();
      injectEmailSidebar(data);
    }
  } catch (e) {
    console.warn('[PhishGuard] Email scan failed:', e);
  }
}

function injectEmailSidebar(data: any): void {
  // Remove existing sidebar
  document.querySelector('[data-phishguard-email]')?.remove();

  const sidebar = document.createElement('div');
  sidebar.setAttribute('data-phishguard-email', 'sidebar');

  const linkResults = (data.link_results || []).map((r: any) => {
    const color = r.risk_level === 'malicious' ? '#EF4444' :
                  r.risk_level === 'suspicious' ? '#F59E0B' : '#22C55E';
    const url = r.url || '';
    const shortUrl = url.length > 40 ? url.substring(0, 40) + '...' : url;
    return `
      <div style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
        <div style="display: flex; align-items: center; gap: 6px;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color}; flex-shrink: 0;"></span>
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #CBD5E1; word-break: break-all;">${shortUrl}</span>
        </div>
        <div style="font-size: 11px; color: ${color}; margin-top: 2px; padding-left: 14px;">
          ${r.risk_level?.toUpperCase()} — ${((r.risk_score || 0) * 100).toFixed(1)}%
        </div>
      </div>
    `;
  }).join('');

  sidebar.innerHTML = `
    <div style="
      position: fixed; right: 16px; top: 80px; z-index: 2147483647;
      width: 300px; max-height: 500px; overflow-y: auto;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(16px) saturate(180%);
      border: 1px solid rgba(99, 102, 241, 0.2);
      border-radius: 16px; padding: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      font-family: 'Inter', -apple-system, sans-serif;
      animation: phishguard-slide-in 0.35s ease-out;
    ">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <span style="color: #E2E8F0; font-weight: 600; font-size: 14px;">🛡 PhishGuard</span>
        <button onclick="this.closest('[data-phishguard-email]').remove()" style="
          background: none; border: none; color: #64748B; cursor: pointer; font-size: 16px;
        ">×</button>
      </div>
      <div style="color: #94A3B8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
        Email Link Analysis — ${data.link_results?.length || 0} links
      </div>
      ${linkResults || '<div style="color: #64748B; font-size: 13px;">No links found</div>'}
    </div>
  `;

  document.body.appendChild(sidebar);
}

// Observe DOM changes to detect when emails are opened
const observer = new MutationObserver(() => {
  const links = extractLinks();
  if (links.length > 0) {
    scanEmailLinks();
  }
});

// Start observing after page loads
setTimeout(() => {
  observer.observe(document.body, { childList: true, subtree: true });
}, 2000);

export {};
