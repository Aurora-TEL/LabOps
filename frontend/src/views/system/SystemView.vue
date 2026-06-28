<script setup lang="ts">
import { ListChecks, RefreshCw, ShieldCheck, UserCog, Users, Workflow } from 'lucide-vue-next';
import { computed, onMounted, reactive, ref } from 'vue';

import {
  getSystemPermissions,
  getSystemRoles,
  getSystemSummary,
  getSystemUsers,
  updateSystemUserRoles,
  updateSystemUserStatus,
  type SystemUserStatus
} from '@/api/system';
import { useNotificationsStore } from '@/stores/notifications';
import type { SystemPermission, SystemRole, SystemSummary, SystemUser } from '@/types';

const notificationsStore = useNotificationsStore();
const activeTab = ref<'users' | 'roles' | 'audit'>('users');
const loading = ref(false);
const actionLoading = ref('');
const error = ref('');
const success = ref('');
const users = ref<SystemUser[]>([]);
const roles = ref<SystemRole[]>([]);
const permissions = ref<SystemPermission[]>([]);
const summary = ref<SystemSummary>({
  user_total: 0,
  active_users: 0,
  disabled_users: 0,
  role_total: 0,
  permission_total: 0
});
const filters = reactive({
  keyword: '',
  status: '' as SystemUserStatus | '',
  role_code: ''
});
const roleDrafts = reactive<Record<string, string[]>>({});
const recentOperations = computed(() => notificationsStore.recentOperations.slice(0, 8));

const settings = [
  { icon: UserCog, title: '角色权限', text: '管理员、设备负责人、普通用户三类核心角色已接入菜单、按钮和接口权限。' },
  { icon: Workflow, title: '审批流程', text: '预约审核、报修派工、维修验收流程保留配置入口，可继续扩展审批节点。' },
  { icon: ShieldCheck, title: '数据安全', text: '登录态、接口鉴权、通知中心和操作审计共同组成演示级安全闭环。' }
];

const tabs = [
  { key: 'users', label: '用户管理', icon: Users },
  { key: 'roles', label: '角色权限', icon: ShieldCheck },
  { key: 'audit', label: '操作审计', icon: ListChecks }
] as const;

const metricCards = computed(() => [
  { label: '用户总数', value: summary.value.user_total, unit: '人' },
  { label: '启用用户', value: summary.value.active_users, unit: '人' },
  { label: '系统角色', value: summary.value.role_total, unit: '类' },
  { label: '权限点', value: summary.value.permission_total, unit: '项' }
]);

const permissionGroups = computed(() => {
  const groups: Record<string, SystemPermission[]> = {};
  permissions.value.forEach((permission) => {
    groups[permission.resource] = groups[permission.resource] || [];
    groups[permission.resource].push(permission);
  });
  return Object.entries(groups).map(([resource, items]) => ({
    resource,
    permissions: items.sort((a, b) => a.code.localeCompare(b.code))
  }));
});

function roleLabel(role: SystemRole) {
  return role.name || role.code;
}

function statusLabel(status: SystemUserStatus) {
  return { active: '启用', disabled: '停用', locked: '锁定' }[status];
}

function statusClass(status: SystemUserStatus) {
  return `status-${status}`;
}

function syncRoleDrafts() {
  users.value.forEach((user) => {
    roleDrafts[user.id] = user.roles.map((role) => role.code);
  });
}

async function loadSystemData() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryData, userPage, roleData, permissionData] = await Promise.all([
      getSystemSummary(),
      getSystemUsers(filters),
      getSystemRoles(),
      getSystemPermissions()
    ]);
    summary.value = summaryData;
    users.value = userPage.items;
    roles.value = roleData;
    permissions.value = permissionData;
    syncRoleDrafts();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '系统管理数据加载失败';
  } finally {
    loading.value = false;
  }
}

async function changeStatus(user: SystemUser, status: SystemUserStatus) {
  actionLoading.value = `${user.id}:status`;
  error.value = '';
  success.value = '';
  try {
    const updated = await updateSystemUserStatus(user.id, status);
    users.value = users.value.map((item) => (item.id === updated.id ? updated : item));
    success.value = `已更新 ${updated.real_name} 的账号状态`;
    await loadSystemData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '账号状态更新失败';
  } finally {
    actionLoading.value = '';
  }
}

async function saveRoles(user: SystemUser) {
  actionLoading.value = `${user.id}:roles`;
  error.value = '';
  success.value = '';
  try {
    const updated = await updateSystemUserRoles(user.id, roleDrafts[user.id] || []);
    users.value = users.value.map((item) => (item.id === updated.id ? updated : item));
    roleDrafts[user.id] = updated.roles.map((role) => role.code);
    success.value = `已更新 ${updated.real_name} 的角色`;
    await loadSystemData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '角色更新失败';
  } finally {
    actionLoading.value = '';
  }
}

onMounted(() => {
  void loadSystemData();
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
        <h1>系统设置与权限中心</h1>
        <p class="subtle">用于答辩展示的后台管理入口，强调账号、角色、权限和关键操作可追踪。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ loading ? '加载中' : '后端接口' }}</span>
        <button class="text-button" type="button" :disabled="loading" @click="loadSystemData"><RefreshCw :size="17" />刷新</button>
      </div>
    </section>

    <section class="setting-grid">
      <article v-for="item in settings" :key="item.title" class="panel setting-card">
        <span><component :is="item.icon" :size="24" /></span>
        <h2>{{ item.title }}</h2>
        <p>{{ item.text }}</p>
      </article>
    </section>

    <section class="grid metrics">
      <div v-for="item in metricCards" :key="item.label" class="panel system-metric">
        <strong>{{ item.value }}</strong>
        <span>{{ item.label }} / {{ item.unit }}</span>
      </div>
    </section>

    <div v-if="error" class="data-state warning">{{ error }}</div>
    <div v-if="success" class="success-state">{{ success }}</div>

    <section class="panel system-console">
      <div class="tabbar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-button"
          :class="{ active: activeTab === tab.key }"
          type="button"
          @click="activeTab = tab.key"
        >
          <component :is="tab.icon" :size="17" />{{ tab.label }}
        </button>
      </div>

      <div v-if="activeTab === 'users'" class="console-body">
        <div class="filter-row">
          <input v-model.trim="filters.keyword" class="field" placeholder="搜索用户名、姓名、院系" @keyup.enter="loadSystemData" />
          <select v-model="filters.status" class="field" @change="loadSystemData">
            <option value="">全部状态</option>
            <option value="active">启用</option>
            <option value="disabled">停用</option>
            <option value="locked">锁定</option>
          </select>
          <select v-model="filters.role_code" class="field" @change="loadSystemData">
            <option value="">全部角色</option>
            <option v-for="role in roles" :key="role.id" :value="role.code">{{ roleLabel(role) }}</option>
          </select>
          <button class="text-button primary" type="button" :disabled="loading" @click="loadSystemData">查询</button>
        </div>

        <div class="table-wrap">
          <table class="table user-table">
            <thead>
              <tr>
                <th>用户</th>
                <th>院系/联系方式</th>
                <th>状态</th>
                <th>角色授权</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <strong>{{ user.real_name }}</strong>
                  <span>{{ user.username }}</span>
                </td>
                <td>
                  <strong>{{ user.department || '未设置院系' }}</strong>
                  <span>{{ user.email || user.phone || '未设置联系方式' }}</span>
                </td>
                <td>
                  <span class="status-chip" :class="statusClass(user.status)">{{ statusLabel(user.status) }}</span>
                  <select class="mini-select" :value="user.status" :disabled="Boolean(actionLoading)" @change="changeStatus(user, ($event.target as HTMLSelectElement).value as SystemUserStatus)">
                    <option value="active">启用</option>
                    <option value="disabled">停用</option>
                    <option value="locked">锁定</option>
                  </select>
                </td>
                <td>
                  <div class="role-checks">
                    <label v-for="role in roles" :key="role.id">
                      <input v-model="roleDrafts[user.id]" type="checkbox" :value="role.code" />
                      {{ roleLabel(role) }}
                    </label>
                  </div>
                </td>
                <td>
                  <button class="mini-button primary" type="button" :disabled="Boolean(actionLoading)" @click="saveRoles(user)">保存角色</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab === 'roles'" class="console-body role-grid">
        <article v-for="role in roles" :key="role.id" class="role-panel">
          <div class="role-head">
            <div>
              <strong>{{ roleLabel(role) }}</strong>
              <span>{{ role.code }} / {{ role.user_count }} 人</span>
            </div>
            <small>{{ role.is_system ? '系统角色' : '自定义角色' }}</small>
          </div>
          <div class="permission-tags">
            <span v-for="permission in role.permissions" :key="permission.id">{{ permission.code }}</span>
          </div>
        </article>

        <section class="permission-matrix">
          <h2>权限点矩阵</h2>
          <div class="permission-groups">
            <div v-for="group in permissionGroups" :key="group.resource" class="permission-group">
              <strong>{{ group.resource }}</strong>
              <span v-for="permission in group.permissions" :key="permission.id">{{ permission.action }}</span>
            </div>
          </div>
        </section>
      </div>

      <div v-if="activeTab === 'audit'" class="console-body">
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

.setting-card,
.system-metric {
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

.system-metric {
  display: flex;
  min-height: 96px;
  flex-direction: column;
  justify-content: center;
}

.system-metric strong {
  color: var(--blue);
  font-size: 30px;
}

.system-metric span,
.role-head span,
.role-head small,
.audit-item span,
.audit-item p,
.audit-item small,
.empty-text {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.system-console {
  overflow: hidden;
}

.tabbar {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #edf2f7;
  background: #f8fbff;
  padding: 12px;
}

.tab-button {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 36px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: #40516a;
  padding: 0 14px;
  font-weight: 900;
}

.tab-button.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
  color: #fff;
}

.console-body {
  padding: 18px;
}

.filter-row {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 150px 180px auto;
  gap: 10px;
  margin-bottom: 14px;
}

.user-table th:nth-child(1) {
  width: 190px;
}

.user-table th:nth-child(3) {
  width: 150px;
}

.user-table th:nth-child(5) {
  width: 110px;
}

.user-table strong,
.audit-item strong {
  display: block;
  color: #1d2a3e;
}

.user-table td > span {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.status-chip {
  display: inline-flex;
  min-height: 26px;
  align-items: center;
  border-radius: 999px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 900;
}

.status-active {
  background: #ecfbf5;
  color: #0a7d4f;
}

.status-disabled {
  background: #f2f5f8;
  color: #66758d;
}

.status-locked {
  background: #fff3e0;
  color: #a86200;
}

.mini-select {
  width: 100%;
  min-height: 30px;
  margin-top: 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: #304057;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 800;
}

.role-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.role-checks label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #40516a;
  font-size: 12px;
  font-weight: 800;
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.role-panel,
.permission-matrix {
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.role-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.role-head strong {
  display: block;
  color: #172033;
}

.role-head small {
  flex: 0 0 auto;
}

.permission-tags,
.permission-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.permission-tags span,
.permission-group span {
  border-radius: 999px;
  background: #eaf3ff;
  color: #275a9f;
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 900;
}

.permission-matrix {
  grid-column: 1 / -1;
}

.permission-group {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: center;
  width: 100%;
}

.permission-group strong {
  min-width: 110px;
  color: #1d2a3e;
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

@media (max-width: 1080px) {
  .setting-grid,
  .role-grid {
    grid-template-columns: 1fr;
  }

  .filter-row,
  .audit-item {
    grid-template-columns: 1fr;
  }

  .tabbar {
    overflow-x: auto;
  }
}
</style>
