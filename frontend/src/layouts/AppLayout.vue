<script setup lang="ts">
import {
  BarChart3,
  Bell,
  CalendarClock,
  Factory,
  Gauge,
  LayoutDashboard,
  LogOut,
  Menu,
  MonitorCog,
  Search,
  Settings,
  UserRoundCheck,
  Wrench
} from 'lucide-vue-next';
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/stores/auth';
import { useOperationsStore } from '@/stores/operations';

const route = useRoute();
const router = useRouter();
const collapsed = ref(false);
const operationsStore = useOperationsStore();
const authStore = useAuthStore();

const allNavItems = [
  { label: '我的预约', path: '/ordinary', icon: UserRoundCheck, roles: ['ordinary_user', 'student'] },
  { label: '负责人工作台', path: '/owner', icon: Gauge, roles: ['device_owner'] },
  { label: '运营首页', path: '/dashboard', icon: LayoutDashboard, permissions: ['dashboard:view'] },
  { label: '设备状态', path: '/devices', icon: MonitorCog, permissions: ['device:view'] },
  { label: '预约管理', path: '/reservations', icon: CalendarClock, permissions: ['reservation:view_self', 'reservation:view_all'] },
  { label: '报修工单', path: '/repairs', icon: Wrench, permissions: ['repair:view_self', 'repair:view_all'] },
  { label: '数据分析', path: '/analytics', icon: BarChart3, permissions: ['analytics:view'] },
  { label: '系统设置', path: '/system', icon: Settings, permissions: ['user:manage', 'role:manage'] }
];

const navItems = computed(() =>
  allNavItems.filter((item) => {
    if (!authStore.isAdminUser) {
      if (authStore.isDeviceOwner) return item.path === '/owner';
      if (authStore.isOrdinaryUser) return item.path === '/ordinary';
    }
    if ('roles' in item && item.roles) return authStore.hasAnyRole(item.roles);
    if ('permissions' in item && item.permissions) return authStore.hasAnyPermission(item.permissions);
    return true;
  })
);
const title = computed(() => String(route.meta.title ?? '运营首页'));
const avatarText = computed(() => authStore.displayName.slice(0, 1));
const shellLabel = computed(() => {
  if (authStore.isDeviceOwner && !authStore.isAdminUser) return '设备运维中心';
  if (authStore.isOrdinaryUser && !authStore.isAdminUser) return '实验预约自助台';
  return '实验室运营中心';
});

async function signOut() {
  await authStore.signOut();
  await router.replace('/login');
}

onMounted(() => {
  if (!authStore.initialized) {
    void authStore.loadCurrentUser();
  }
  if (!operationsStore.loaded) {
    void operationsStore.load();
  }
});
</script>

<template>
  <div class="shell" :class="{ collapsed }">
    <aside class="sidebar">
      <RouterLink class="brand" :to="authStore.landingPath" aria-label="LabOps">
        <span class="brand-mark"><Factory :size="22" /></span>
        <span class="brand-text">
          <strong>LabOps</strong>
          <small>{{ shellLabel }}</small>
        </span>
      </RouterLink>

      <nav class="nav">
        <RouterLink v-for="item in navItems" :key="item.path" class="nav-link" :to="item.path">
          <component :is="item.icon" :size="19" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="side-summary">
        <Gauge :size="24" />
        <div>
          <strong>78.9%</strong>
          <span>综合 OEE</span>
        </div>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="topbar-left">
          <button class="icon-button" type="button" title="折叠菜单" @click="collapsed = !collapsed">
            <Menu :size="20" />
          </button>
          <div>
            <p class="top-kicker">{{ shellLabel }}</p>
            <h1>{{ title }}</h1>
          </div>
        </div>

        <div class="topbar-actions">
          <label class="search-box">
            <Search :size="18" />
            <input placeholder="搜索设备、预约、工单" />
          </label>
          <button class="icon-button" type="button" title="消息通知">
            <Bell :size="19" />
          </button>
          <div class="user-chip">
            <span>{{ avatarText }}</span>
            <div>
              <strong>{{ authStore.displayName }}</strong>
              <small>{{ authStore.roleLabel }}</small>
            </div>
          </div>
          <button class="icon-button" type="button" title="退出登录" @click="signOut">
            <LogOut :size="18" />
          </button>
        </div>
      </header>

      <main class="content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 252px minmax(0, 1fr);
  background:
    linear-gradient(120deg, rgba(245, 250, 255, 0.92), rgba(234, 243, 252, 0.9)),
    repeating-linear-gradient(90deg, rgba(23, 105, 224, 0.04) 0 1px, transparent 1px 80px);
}

.sidebar {
  position: sticky;
  top: 0;
  display: flex;
  height: 100vh;
  flex-direction: column;
  border-right: 1px solid rgba(202, 216, 234, 0.9);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px);
  padding: 20px 14px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 54px;
  padding: 0 10px;
}

.brand-mark {
  display: inline-flex;
  width: 42px;
  height: 42px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
  box-shadow: 0 12px 26px rgba(23, 105, 224, 0.24);
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-text strong {
  font-size: 19px;
}

.brand-text small {
  color: var(--muted);
  font-size: 12px;
}

.nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  margin-top: 26px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
  border-radius: 8px;
  padding: 0 12px;
  color: #4b5a70;
  font-weight: 700;
}

.nav-link.router-link-active {
  color: #fff;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
  box-shadow: 0 12px 24px rgba(23, 105, 224, 0.2);
}

.side-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #dce7f4;
  border-radius: 8px;
  padding: 14px;
  color: var(--blue);
  background: #f5faff;
}

.side-summary div {
  display: flex;
  flex-direction: column;
}

.side-summary strong {
  color: #172033;
  font-size: 20px;
}

.side-summary span {
  color: var(--muted);
  font-size: 12px;
}

.main {
  min-width: 0;
}

.topbar {
  position: sticky;
  z-index: 10;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 82px;
  border-bottom: 1px solid rgba(209, 221, 236, 0.84);
  background: rgba(246, 250, 255, 0.82);
  backdrop-filter: blur(16px);
  padding: 14px 24px;
}

.topbar-left,
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.top-kicker {
  margin: 0 0 2px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.topbar h1 {
  margin: 0;
  font-size: 22px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  width: min(320px, 28vw);
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 0 12px;
  color: var(--muted);
}

.search-box input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  color: #243249;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 6px 10px 6px 6px;
}

.user-chip > span {
  display: inline-flex;
  width: 30px;
  height: 30px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  background: #243249;
  font-weight: 900;
}

.user-chip div {
  display: flex;
  flex-direction: column;
  white-space: nowrap;
}

.user-chip strong {
  font-size: 13px;
}

.user-chip small {
  color: var(--muted);
  font-size: 12px;
}

.content {
  padding: 24px;
}

.collapsed {
  grid-template-columns: 84px minmax(0, 1fr);
}

.collapsed .brand-text,
.collapsed .nav-link span,
.collapsed .side-summary div {
  display: none;
}

.collapsed .nav-link,
.collapsed .brand {
  justify-content: center;
}

@media (max-width: 900px) {
  .shell,
  .collapsed {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
    padding: 12px;
  }

  .nav {
    flex-direction: row;
    overflow-x: auto;
    margin-top: 12px;
  }

  .nav-link {
    flex: 0 0 auto;
  }

  .side-summary {
    display: none;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .topbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .search-box {
    width: 100%;
  }
}
</style>
