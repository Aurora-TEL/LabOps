<script setup lang="ts">
import { ListChecks, ShieldCheck, UserCog, Workflow } from 'lucide-vue-next';
import { computed, onMounted } from 'vue';

import { useNotificationsStore } from '@/stores/notifications';

const notificationsStore = useNotificationsStore();
const recentOperations = computed(() => notificationsStore.recentOperations.slice(0, 6));

const settings = [
  { icon: UserCog, title: '角色权限', text: '管理员、设备负责人、普通用户三类核心角色已接入菜单、按钮和接口权限。' },
  { icon: Workflow, title: '审批流程', text: '预约审核、报修派工、维修验收流程保留配置入口，可继续扩展审批节点。' },
  { icon: ShieldCheck, title: '数据安全', text: '登录态、接口鉴权、通知中心和操作审计共同组成演示级安全闭环。' }
];

onMounted(() => {
  if (!notificationsStore.loaded) {
    void notificationsStore.load();
  }
});
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">平台管理</p>
        <h1>系统设置与审计中心</h1>
        <p class="subtle">用于答辩展示的后台管理入口，强调角色权限、业务流程和关键操作可追踪。</p>
      </div>
    </section>

    <section class="setting-grid">
      <article v-for="item in settings" :key="item.title" class="panel setting-card">
        <span><component :is="item.icon" :size="24" /></span>
        <h2>{{ item.title }}</h2>
        <p>{{ item.text }}</p>
      </article>
    </section>

    <section class="panel audit-panel">
      <div class="panel-header">
        <h2><ListChecks :size="19" />最近操作日志</h2>
        <span class="source-badge">{{ notificationsStore.source === 'api' ? '后端审计' : '演示数据' }}</span>
      </div>
      <div class="audit-list">
        <article v-for="item in recentOperations" :key="item.id" class="audit-item">
          <div>
            <strong>{{ item.action }}</strong>
            <span>{{ item.actor }} / {{ item.target }}</span>
          </div>
          <p>{{ item.detail }}</p>
          <small :class="item.status">{{ item.createdAt }}</small>
        </article>
        <div v-if="recentOperations.length === 0" class="empty-text">暂无审计日志</div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.setting-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.setting-card {
  padding: 22px;
}

.setting-card > span {
  display: inline-flex;
  width: 46px;
  height: 46px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
}

.setting-card h2 {
  margin-top: 18px;
}

.setting-card p {
  margin-bottom: 0;
  color: var(--muted);
  line-height: 1.7;
}

.audit-panel {
  margin-top: 16px;
}

.panel-header h2 {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.audit-list {
  display: grid;
  gap: 12px;
}

.audit-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(180px, 1.4fr) auto;
  gap: 14px;
  align-items: center;
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.audit-item strong {
  display: block;
  color: #1d2a3e;
}

.audit-item span,
.audit-item p,
.audit-item small,
.empty-text {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.audit-item p {
  margin: 0;
  font-weight: 700;
}

.audit-item small.success {
  color: #169b62;
}

.audit-item small.warning {
  color: #d28700;
}

.audit-item small.failed {
  color: #d64545;
}

.empty-text {
  padding: 24px;
  text-align: center;
}

@media (max-width: 900px) {
  .setting-grid,
  .audit-item {
    grid-template-columns: 1fr;
  }
}
</style>
