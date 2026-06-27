import { clearStoredToken, requestApi, setStoredToken } from '@/api/client';

export interface CurrentUser {
  id: string;
  username: string;
  real_name: string;
  roles: string[];
  permissions: string[];
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: CurrentUser;
}

export async function login(username: string, password: string) {
  const result = await requestApi<LoginResult>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  setStoredToken(result.access_token);
  return result;
}

export async function getCurrentUser() {
  return requestApi<CurrentUser>('/auth/me');
}

export async function logout() {
  try {
    await requestApi<{ revoked: boolean }>('/auth/logout', { method: 'POST' });
  } finally {
    clearStoredToken();
  }
}
