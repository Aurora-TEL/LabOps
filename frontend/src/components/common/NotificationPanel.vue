<script setup lang="ts">
import { Bell, CheckCheck, Circle, Loader2 } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

import { useNotificationsStore } from '@/stores/notifications';
import type { NotificationItem, NotificationType } from '@/types';

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useNotificationsStore();
const { data, loading, error, source, actionLoading } = storeToRefs(store);

const typeLabels: Record<NotificationType, string> = {
  reservation: '预约',
  repair: '报修',
  work_order: '工单',
  system: '系统'
};

const notifications = computed(() => data.value.notifications.slice(0, 8));

function typeLabel(type: NotificationType) {
  return typeLabels[type] ?? type;
}

function statusLabel(item: NotificationItem) {
  return item.read ? '已读' : '未读';
}
</script>

<template>
  <div v-if="props.open" class="notification-popover">
    <div class="notification-head">
      <div>
        <strong>消息通知</strong>
        <span>{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
      </div>
      <button class="mini-button" type="button" :disabled="actionLoading === 'all'" @click="store.markAllRead">
        <CheckCheck :size="14" />全部已读
      </button>
    </div>

    <div v-if="error" class="notification-error">{{ error }}</div>
    <div v-if="loading" class="notification-loading"><Loader2 :size="16" />加载通知中</div>

    <div v-else class="notification-list">
      <article v-for="item in notifications" :key="item.id" class="notification-item" :class="{ unread: !item.read }">
        <div class="notification-title">
          <span><Bell :size="15" />{{ item.title }}</span>
          <small>{{ typeLabel(item.type) }}</small>
        </div>
        <p>{{ item.content }}</p>
        <div class="notification-meta">
          <span>{{ item.createdAt }}</span>
          <span class="read-state"><Circle :size="9" />{{ statusLabel(item) }}</span>
        </div>
        <div class="notification-actions">
          <RouterLink v-if="item.link" class="mini-button" :to="item.link" @click="emit('close')">查看</RouterLink>
          <button class="mini-button primary" type="button" :disabled="item.read || actionLoading === item.id" @click="store.markRead(item)">
            标为已读
          </button>
        </div>
      </article>
      <div v-if="notifications.length === 0" class="notification-empty">暂无消息通知</div>
    </div>
  </div>
</template>

<style scoped>
.notification-popover {
  position: absolute;
  z-index: 30;
  top: calc(100% + 10px);
  right: 0;
  width: min(420px, calc(100vw - 32px));
  border: 1px solid rgba(190, 205, 225, 0.92);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 48px rgba(26, 57, 96, 0.18);
  padding: 12px;
}

.notification-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 4px 4px 10px;
}

.notification-head div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.notification-head strong {
  color: #172033;
  font-size: 15px;
}

.notification-head span,
.notification-meta,
.notification-error,
.notification-loading,
.notification-empty {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.notification-error {
  margin-bottom: 10px;
  border: 1px solid #f7d7a3;
  border-radius: 8px;
  background: #fff8ec;
  color: #9a5d00;
  padding: 9px 10px;
}

.notification-loading,
.notification-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 82px;
}

.notification-loading svg {
  animation: spin 1s linear infinite;
}

.notification-list {
  display: flex;
  max-height: 520px;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
}

.notification-item {
  display: grid;
  gap: 8px;
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 12px;
}

.notification-item.unread {
  border-color: #c9def8;
  background: #f5faff;
}

.notification-title,
.notification-title span,
.notification-meta,
.notification-actions,
.read-state {
  display: flex;
  align-items: center;
}

.notification-title {
  justify-content: space-between;
  gap: 10px;
}

.notification-title span {
  min-width: 0;
  gap: 7px;
  color: #1d2a3e;
  font-weight: 900;
}

.notification-title small {
  flex: 0 0 auto;
  border-radius: 999px;
  background: #e8f5f8;
  color: #376071;
  padding: 3px 8px;
  font-size: 12px;
  font-weight: 900;
}

.notification-item p {
  margin: 0;
  color: #40516a;
  font-size: 13px;
  line-height: 1.55;
}

.notification-meta {
  justify-content: space-between;
  gap: 10px;
}

.read-state {
  gap: 5px;
}

.unread .read-state {
  color: var(--blue);
}

.notification-actions {
  justify-content: flex-end;
  gap: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
