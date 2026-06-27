import { createRouter, createWebHistory } from 'vue-router';

import AppLayout from '@/layouts/AppLayout.vue';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { public: true, title: '登录' }
    },
    {
      path: '/',
      component: AppLayout,
      redirect: () => {
        const authStore = useAuthStore();
        return authStore.landingPath;
      },
      children: [
        {
          path: 'ordinary',
          name: 'ordinary-workbench',
          component: () => import('@/views/workbenches/OrdinaryWorkbench.vue'),
          meta: { title: '我的实验预约', roles: ['ordinary_user', 'student'] }
        },
        {
          path: 'owner',
          name: 'owner-workbench',
          component: () => import('@/views/workbenches/OwnerWorkbench.vue'),
          meta: { title: '设备负责人工作台', roles: ['device_owner'] }
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { title: '运营首页', permissions: ['dashboard:view'] }
        },
        {
          path: 'devices',
          name: 'devices',
          component: () => import('@/views/devices/DevicesView.vue'),
          meta: { title: '设备状态', permissions: ['device:view'] }
        },
        {
          path: 'reservations',
          name: 'reservations',
          component: () => import('@/views/reservations/ReservationsView.vue'),
          meta: { title: '预约管理', permissions: ['reservation:view_self', 'reservation:view_all'] }
        },
        {
          path: 'repairs',
          name: 'repairs',
          component: () => import('@/views/repairs/RepairsView.vue'),
          meta: { title: '报修工单', permissions: ['repair:view_self', 'repair:view_all'] }
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('@/views/analytics/AnalyticsView.vue'),
          meta: { title: '数据分析', permissions: ['analytics:view'] }
        },
        {
          path: 'system',
          name: 'system',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '系统设置', permissions: ['user:manage', 'role:manage'] }
        }
      ]
    }
  ]
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  if (!authStore.initialized) {
    await authStore.loadCurrentUser();
  }

  if (to.meta.public) {
    if (to.name === 'login' && authStore.isAuthenticated) return authStore.landingPath;
    return true;
  }

  if (!authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }

  if (!authStore.isAdminUser) {
    const roleHome = authStore.isDeviceOwner ? 'owner-workbench' : 'ordinary-workbench';
    if (to.name !== roleHome) return authStore.landingPath;
  }

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles?.length && !authStore.hasAnyRole(allowedRoles)) {
    return authStore.landingPath;
  }

  const allowedPermissions = to.meta.permissions as string[] | undefined;
  if (allowedPermissions?.length && !authStore.hasAnyPermission(allowedPermissions)) {
    return authStore.landingPath;
  }

  return true;
});

export default router;
