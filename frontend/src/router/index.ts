import { createRouter, createWebHistory } from 'vue-router';

import AppLayout from '@/layouts/AppLayout.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { title: '运营首页' }
        },
        {
          path: 'devices',
          name: 'devices',
          component: () => import('@/views/devices/DevicesView.vue'),
          meta: { title: '设备状态' }
        },
        {
          path: 'reservations',
          name: 'reservations',
          component: () => import('@/views/reservations/ReservationsView.vue'),
          meta: { title: '预约管理' }
        },
        {
          path: 'repairs',
          name: 'repairs',
          component: () => import('@/views/repairs/RepairsView.vue'),
          meta: { title: '报修工单' }
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('@/views/analytics/AnalyticsView.vue'),
          meta: { title: '数据分析' }
        },
        {
          path: 'system',
          name: 'system',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '系统设置' }
        }
      ]
    }
  ]
});

export default router;
