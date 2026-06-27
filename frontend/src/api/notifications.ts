import { requestApi, type PageData } from '@/api/client';
import { notificationCenterData } from '@/mock/notifications';
import type { NotificationCenterData, NotificationItem, NotificationType, RecentOperation } from '@/types';

interface BackendNotification {
  id: string;
  title: string;
  content: string;
  category: 'info' | 'success' | 'warning' | 'error';
  business_type?: string | null;
  business_id?: string | null;
  created_at: string;
  is_read: boolean;
}

interface BackendAuditLog {
  id: string;
  actor_id?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  summary: string;
  detail?: string | null;
  result: 'success' | 'failure';
  created_at: string;
}

export interface NotificationCenterLoadResult {
  data: NotificationCenterData;
  source: 'api' | 'mock';
  error?: string;
}

const businessTypeMap: Record<string, NotificationType> = {
  reservation: 'reservation',
  repair: 'repair',
  repair_report: 'repair',
  work_order: 'work_order',
  system: 'system'
};

const linkMap: Record<NotificationType, string> = {
  reservation: '/reservations',
  repair: '/repairs',
  work_order: '/repairs',
  system: '/system'
};

function mapNotification(item: BackendNotification): NotificationItem {
  const type = businessTypeMap[item.business_type ?? 'system'] ?? 'system';
  return {
    id: item.id,
    title: item.title,
    content: item.content,
    type,
    createdAt: item.created_at,
    read: item.is_read,
    link: linkMap[type]
  };
}

function mapAuditLog(item: BackendAuditLog): RecentOperation {
  return {
    id: item.id,
    actor: item.actor_id ? item.actor_id.slice(0, 8) : 'system',
    action: item.action,
    target: item.resource_type,
    detail: item.detail || item.summary,
    createdAt: item.created_at,
    status: item.result === 'success' ? 'success' : 'failed'
  };
}

export async function getNotificationCenterData(): Promise<NotificationCenterLoadResult> {
  try {
    const notificationsPage = await requestApi<PageData<BackendNotification>>('/notifications?page_size=20');
    let recentOperations: RecentOperation[] = [];
    try {
      const auditPage = await requestApi<PageData<BackendAuditLog>>('/audit-logs?page_size=10');
      recentOperations = auditPage.items.map(mapAuditLog);
    } catch {
      recentOperations = notificationCenterData.recentOperations;
    }

    return {
      data: {
        notifications: notificationsPage.items.map(mapNotification),
        recentOperations
      },
      source: 'api'
    };
  } catch (error) {
    return {
      data: notificationCenterData,
      source: 'mock',
      error: error instanceof Error ? `${error.message}，已切换演示数据` : '通知接口暂不可用，已切换演示数据'
    };
  }
}

export function markNotificationRead(notificationId: string) {
  return requestApi<BackendNotification>(`/notifications/${notificationId}/read`, { method: 'PATCH' });
}

export function markAllNotificationsRead() {
  return requestApi<{ updated: number }>('/notifications/read-all', { method: 'PATCH' });
}
