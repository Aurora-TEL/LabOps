import { requestApi, type PageData } from '@/api/client';
import type { SystemPermission, SystemRole, SystemSummary, SystemUser } from '@/types';

export type SystemUserStatus = SystemUser['status'];

export function getSystemSummary() {
  return requestApi<SystemSummary>('/system/summary');
}

export function getSystemUsers(params: { keyword?: string; status?: SystemUserStatus | ''; role_code?: string; page_size?: number } = {}) {
  const search = new URLSearchParams();
  search.set('page_size', String(params.page_size ?? 50));
  if (params.keyword) search.set('keyword', params.keyword);
  if (params.status) search.set('status', params.status);
  if (params.role_code) search.set('role_code', params.role_code);
  return requestApi<PageData<SystemUser>>(`/system/users?${search.toString()}`);
}

export function getSystemRoles() {
  return requestApi<SystemRole[]>('/system/roles');
}

export function getSystemPermissions() {
  return requestApi<SystemPermission[]>('/system/permissions');
}

export function updateSystemUserStatus(userId: string, status: SystemUserStatus) {
  return requestApi<SystemUser>(`/system/users/${userId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
}

export function updateSystemUserRoles(userId: string, roleCodes: string[]) {
  return requestApi<SystemUser>(`/system/users/${userId}/roles`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role_codes: roleCodes })
  });
}
