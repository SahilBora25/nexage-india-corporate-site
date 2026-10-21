
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

type ApiError = {
  detail?: string;
  error?: string;
  [key: string]: unknown;
};

async function readApiObject(response: Response): Promise<ApiError | null> {
  const payload: unknown = await response.json().catch(() => null);
  if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
    return null;
  }
  return payload as ApiError;
}

export async function submitEnquiry(
  kind: 'contact' | 'quote',
  data: FormData,
  idempotencyKey?: string
) {
  const endpoint =
    kind === 'quote' ? '/enquiries/quote/' : '/enquiries/contact/';

  let csrfToken: string;

  try {
    const result = await getCsrf();
    csrfToken = result.csrfToken;

    if (!csrfToken) {
      throw new Error('The security token was not returned by the server.');
    }
  } catch {
    throw new Error(
      'Could not obtain the security token. Please refresh the page and try again.'
    );
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      body: data,
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        'X-CSRFToken': csrfToken,
        ...(kind === 'quote' && idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {}),
      },
    });
  } catch {
    throw new Error(
      'We could not connect to the enquiry service. Please try again or email sales@nexageindia.com.'
    );
  }

  const payload = await readApiObject(response);

  if (!response.ok) {
    const msg =
      typeof payload?.detail === 'string'
        ? payload.detail
        : typeof payload?.error === 'string'
          ? payload.error
          : 'Your request could not be submitted. Please check the fields and try again.';

    throw new Error(msg);
  }

  if (!payload) {
    throw new Error(
      'The enquiry service returned an invalid response. Please try again or email sales@nexageindia.com.'
    );
  }

  return payload;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE}${path}`, {
      credentials: 'include',
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new Error('Cannot connect to the admin API. Check that the backend is running.');
  }

  const payload = await readApiObject(response);

  if (!response.ok) {
    throw new Error(
      payload?.detail || 'The request failed.'
    );
  }

  if (!payload) {
    throw new Error('The admin service returned an invalid response.');
  }

  return payload as T;
}

export async function getCsrf() {
  return apiRequest<{ csrfToken: string }>('/auth/csrf/');
}
