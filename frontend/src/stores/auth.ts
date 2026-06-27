import { defineStore } from 'pinia';

import { getCurrentUser, login, logout, type CurrentUser } from '@/api/auth';
import { clearStoredToken, getStoredToken } from '@/api/client';

const roleLabels: Record<string, string> = {
  ordinary_user: '普通用户',
  device_owner: '设备负责人',
  student: '学生',
  teacher: '教师',
  lab_admin: '实验室管理员',
  system_admin: '系统管理员'
};

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getStoredToken(),
    user: null as CurrentUser | null,
    loading: false,
    error: '',
    initialized: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    displayName: (state) => state.user?.real_name || state.user?.username || '演示用户',
    roleLabel: (state) => state.user?.roles.map((role) => roleLabels[role] ?? role).join(' / ') || '未登录',
    isOrdinaryUser: (state) => Boolean(state.user?.roles.includes('ordinary_user') || state.user?.roles.includes('student')),
    isDeviceOwner: (state) => Boolean(state.user?.roles.includes('device_owner')),
    isAdminUser: (state) => Boolean(state.user?.roles.some((role) => ['lab_admin', 'system_admin', 'teacher'].includes(role))),
    landingPath(): string {
      if (this.isAdminUser) return '/dashboard';
      if (this.isDeviceOwner) return '/owner';
      if (this.isOrdinaryUser) return '/ordinary';
      return '/dashboard';
    }
  },
  actions: {
    hasPermission(permission: string) {
      return Boolean(this.user?.permissions.includes(permission));
    },
    hasAnyPermission(permissions: string[]) {
      return permissions.some((permission) => this.hasPermission(permission));
    },
    hasAnyRole(roles: string[]) {
      return Boolean(this.user?.roles.some((role) => roles.includes(role)));
    },
    async signIn(username: string, password: string) {
      this.loading = true;
      this.error = '';
      try {
        const result = await login(username, password);
        this.token = result.access_token;
        this.user = result.user;
        this.initialized = true;
      } catch (error) {
        this.error = error instanceof Error ? error.message : '登录失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async loadCurrentUser() {
      if (!this.token) {
        this.initialized = true;
        return;
      }

      this.loading = true;
      this.error = '';
      try {
        this.user = await getCurrentUser();
      } catch (error) {
        clearStoredToken();
        this.token = null;
        this.user = null;
        this.error = error instanceof Error ? error.message : '登录状态已失效';
      } finally {
        this.initialized = true;
        this.loading = false;
      }
    },
    async signOut() {
      await logout();
      this.token = null;
      this.user = null;
      this.error = '';
      this.initialized = true;
    }
  }
});
