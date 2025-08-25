// Helper to get CSRF token from cookies
export function getCSRFToken() {
  const match = document.cookie.match(new RegExp('(^| )csrf_token=([^;]+)'));
  return match ? match[2] : null;
}

// Generic GET request
export async function getRequest(url) {
  const res = await fetch(url, {
    credentials: 'include', // send cookies
  });

  if (!res.ok) {
    const error = await res.json();
    throw error;
  }

  return res.json();
}

// Generic POST/PUT/DELETE request
export async function sendRequest(url, method = 'POST', data = null) {
  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken(),
  };

  const res = await fetch(url, {
    method,
    headers,
    credentials: 'include',
    body: data ? JSON.stringify(data) : null,
  });

  if (!res.ok) {
    const error = await res.json();
    throw error;
  }

  return res.json();
}