import { defineStore } from 'pinia';

import { getNotificationCenterData, markAllNotificationsRead, markNotificationRead } from '@/api/notifications';
import { notificationCenterData } from '@/mock/notifications';
import type { NotificationCenterData, NotificationItem, NotificationType } from '@/types';

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    data: notificationCenterData as NotificationCenterData,
    loading: false,
    actionLoading: '',
    error: '',
    source: 'mock' as 'api' | 'mock',
    loaded: false
  }),
  getters: {
    unreadCount: (state) => state.data.notifications.filter((item) => !item.read).length,
    recentOperations: (state) => state.data.recentOperations
  },
  actions: {
    async load() {
      this.loading = true;
      try {
        const result = await getNotificationCenterData();
        this.data = result.data;
        this.source = result.source;
        this.error = result.error ?? '';
        this.loaded = true;
      } finally {
        this.loading = false;
      }
    },
    byTypes(types: NotificationType[]) {
      return this.data.notifications.filter((item) => types.includes(item.type));
    },
    async markRead(notification: NotificationItem) {
      if (notification.read) return;
      this.actionLoading = notification.id;
      this.error = '';
      try {
        await markNotificationRead(notification.id);
      } catch (error) {
        this.source = 'mock';
        this.error = error instanceof Error ? `${error.message}，仅更新前端展示状态` : '通知接口暂不可用，仅更新前端展示状态';
      } finally {
        notification.read = true;
        this.actionLoading = '';
      }
    },
    async markAllRead() {
      this.actionLoading = 'all';
      this.error = '';
      try {
        await markAllNotificationsRead();
      } catch (error) {
        this.source = 'mock';
        this.error = error instanceof Error ? `${error.message}，仅更新前端展示状态` : '通知接口暂不可用，仅更新前端展示状态';
      } finally {
        this.data.notifications.forEach((item) => {
          item.read = true;
        });
        this.actionLoading = '';
      }
    }
  }
});
