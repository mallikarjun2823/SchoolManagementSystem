const API_BASE = window.API_BASE || 'http://localhost:8000';

const output = document.getElementById('output');
const backendStatus = document.getElementById('backendStatus');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const googleLoginBtn = document.getElementById('googleLoginBtn');
const clearBtn = document.getElementById('clearBtn');

function showResult(value) {
  output.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
}

function setBackendStatus(ok, text) {
  backendStatus.textContent = text;
  backendStatus.classList.remove('pill-warn', 'pill-success');
  backendStatus.classList.add(ok ? 'pill-success' : 'pill-warn');
}

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw data;
  }
  return data;
}

async function pingBackend() {
  try {
    const response = await fetch(`${API_BASE}/api/schema/`);
    setBackendStatus(response.ok, response.ok ? 'Backend: reachable' : 'Backend: schema unavailable');
  } catch {
    setBackendStatus(false, 'Backend: offline');
  }
}

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(registerForm).entries());
  try {
    const data = await postJson('/api/register/', payload);
    showResult({ action: 'register', data });
  } catch (error) {
    showResult({ action: 'register', error });
  }
});

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(loginForm).entries());
  try {
    const data = await postJson('/api/login/', payload);
    showResult({ action: 'login', data });
  } catch (error) {
    showResult({ action: 'login', error });
  }
});

googleLoginBtn.addEventListener('click', () => {
  const clientId = window.GOOGLE_OAUTH_CLIENT_ID;
  if (!clientId || clientId.includes('<GOOGLE_OAUTH_CLIENT_ID>')) {
    showResult('Set GOOGLE_OAUTH_CLIENT_ID before starting Google OAuth.');
    return;
  }

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: `${window.location.origin}/auth/google/callback`,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'offline',
    prompt: 'consent',
  });

  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
});

clearBtn.addEventListener('click', () => {
  showResult('No response yet.');
});

async function handleOAuthCallback() {
  const url = new URL(window.location.href);
  const code = url.searchParams.get('code');
  const error = url.searchParams.get('error');

  if (error) {
    showResult({ action: 'google-oauth', error });
    return;
  }

  if (!code) {
    return;
  }

  showResult('Exchanging Google code with the backend...');
  try {
    const data = await postJson('/api/oauth/google/', { code });
    showResult({ action: 'google-oauth', data });
    window.history.replaceState({}, document.title, '/');
  } catch (exchangeError) {
    showResult({ action: 'google-oauth', error: exchangeError });
  }
}

pingBackend();
handleOAuthCallback();