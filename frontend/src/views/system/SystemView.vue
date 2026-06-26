<script setup lang="ts">
import { ShieldCheck, UserCog, Workflow } from 'lucide-vue-next';

const settings = [
  { icon: UserCog, title: '角色权限', text: '管理员、设备负责人、普通用户三类角色，可扩展菜单和按钮级权限。' },
  { icon: Workflow, title: '审批流程', text: '预约审核、报修派工、维修验收流程预留配置入口。' },
  { icon: ShieldCheck, title: '数据安全', text: '预留登录态、操作日志、接口鉴权和审计策略。' }
];
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">平台管理</p>
        <h1>系统设置规划</h1>
        <p class="subtle">当前为展示态入口，后续与用户、角色、菜单、日志等后端接口对接。</p>
      </div>
    </section>

    <section class="setting-grid">
      <article v-for="item in settings" :key="item.title" class="panel setting-card">
        <span><component :is="item.icon" :size="24" /></span>
        <h2>{{ item.title }}</h2>
        <p>{{ item.text }}</p>
      </article>
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

@media (max-width: 900px) {
  .setting-grid {
    grid-template-columns: 1fr;
  }
}
</style>
