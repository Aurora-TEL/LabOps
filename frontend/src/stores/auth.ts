import { defineStore } from 'pinia';

import { getCurrentUser, login, logout, type CurrentUser } from '@/api/auth';
import { clearStoredToken, getStoredToken } from '@/api/client';

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
    roleLabel: (state) => state.user?.roles.join(' / ') || '未登录'
  },
  actions: {
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
