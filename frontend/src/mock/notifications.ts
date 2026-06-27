import type { NotificationCenterData } from '@/types';

export const notificationCenterData: NotificationCenterData = {
  notifications: [
    {
      id: 'NTF-20260627-001',
      title: '预约已通过',
      content: '3D Printer A01 09:00-11:30 的预约已审核通过，请按时到场。',
      type: 'reservation',
      createdAt: '2026-06-27 09:18',
      read: false,
      link: '/ordinary'
    },
    {
      id: 'NTF-20260627-002',
      title: '报修处理中',
      content: 'Laser Cutter L01 的报修已生成维修工单，当前状态为处理中。',
      type: 'repair',
      createdAt: '2026-06-27 10:02',
      read: false,
      link: '/ordinary'
    },
    {
      id: 'NTF-20260627-003',
      title: '新预约待审核',
      content: '普通用户提交了 Network Analyzer NET-01 的预约申请。',
      type: 'reservation',
      createdAt: '2026-06-27 10:24',
      read: false,
      link: '/owner'
    },
    {
      id: 'NTF-20260627-004',
      title: '新报修待处理',
      content: 'Network Analyzer NET-01 出现采集链路间歇断开，请负责人确认。',
      type: 'repair',
      createdAt: '2026-06-27 10:31',
      read: true,
      link: '/owner'
    },
    {
      id: 'NTF-20260627-005',
      title: '工单提醒',
      content: 'WO-20260626-019 已处理超过 2 小时，请更新维修进度。',
      type: 'work_order',
      createdAt: '2026-06-27 11:08',
      read: false,
      link: '/owner'
    },
    {
      id: 'NTF-20260627-006',
      title: '系统巡检完成',
      content: '接口鉴权、菜单权限、设备同步任务巡检完成，无阻断项。',
      type: 'system',
      createdAt: '2026-06-27 11:30',
      read: true,
      link: '/system'
    }
  ],
  recentOperations: [
    {
      id: 'OP-20260627-001',
      actor: 'Lab Admin Demo',
      action: '调整角色权限',
      target: 'device_owner',
      detail: '授予通知查看与已读权限',
      createdAt: '2026-06-27 11:28',
      status: 'success'
    },
    {
      id: 'OP-20260627-002',
      actor: 'Device Owner Demo',
      action: '更新设备状态',
      target: 'Laser Cutter L01',
      detail: '从运行中切换为维护中',
      createdAt: '2026-06-27 10:55',
      status: 'warning'
    },
    {
      id: 'OP-20260627-003',
      actor: 'Ordinary User Demo',
      action: '提交报修',
      target: 'Network Analyzer NET-01',
      detail: '采集链路间歇断开',
      createdAt: '2026-06-27 10:31',
      status: 'success'
    },
    {
      id: 'OP-20260627-004',
      actor: 'System Admin',
      action: '同步设备台账',
      target: '设备主数据',
      detail: '演示环境完成数据刷新',
      createdAt: '2026-06-27 09:40',
      status: 'failed'
    }
  ]
};
