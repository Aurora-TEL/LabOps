import type { WorkbenchData } from '@/types';

export const workbenchData: WorkbenchData = {
  metrics: [
    { label: '今日设备开机率', value: '86.4', unit: '%', trend: 'up', delta: '+4.8%', accent: 'blue' },
    { label: '待审核预约', value: '18', unit: '单', trend: 'down', delta: '-6', accent: 'orange' },
    { label: '处理中工单', value: '27', unit: '项', trend: 'up', delta: '+3', accent: 'violet' },
    { label: '综合 OEE', value: '78.9', unit: '%', trend: 'flat', delta: '持平', accent: 'green' }
  ],
  deviceStatuses: [
    {
      id: 'EQ-1008',
      name: '五轴加工中心',
      workshop: '精密制造一车间',
      status: '运行中',
      utilization: 91,
      temperature: 42,
      nextMaintenance: '2026-07-03'
    },
    {
      id: 'EQ-1021',
      name: '工业机器人臂',
      workshop: '自动化装配线',
      status: '待机',
      utilization: 63,
      temperature: 35,
      nextMaintenance: '2026-07-08'
    },
    {
      id: 'EQ-1037',
      name: '环境试验箱',
      workshop: '可靠性实验室',
      status: '维护中',
      utilization: 38,
      temperature: 29,
      nextMaintenance: '2026-06-28'
    },
    {
      id: 'EQ-1055',
      name: '激光切割机',
      workshop: '钣金加工区',
      status: '运行中',
      utilization: 84,
      temperature: 48,
      nextMaintenance: '2026-07-12'
    }
  ],
  reservations: [
    {
      id: 'RSV-240621',
      device: '环境试验箱',
      applicant: '周若琳',
      department: '质量工程部',
      slot: '09:00-11:30',
      status: '进行中'
    },
    {
      id: 'RSV-240622',
      device: '三坐标测量仪',
      applicant: '陈启明',
      department: '研发中心',
      slot: '13:30-15:00',
      status: '待审核'
    },
    {
      id: 'RSV-240623',
      device: '五轴加工中心',
      applicant: '李思远',
      department: '制造工程部',
      slot: '15:30-18:00',
      status: '已确认'
    }
  ],
  repairReports: [
    {
      id: 'REP-20260626-014',
      device: '五轴加工中心',
      faultType: 'hardware',
      description: '主轴振动值超过预警阈值',
      reporter: '周若琳',
      status: '已派单',
      createdAt: '08:20'
    },
    {
      id: 'REP-20260626-015',
      device: '自动化装配线',
      faultType: 'network',
      description: '扫码枪间歇性断连，影响入库确认',
      reporter: '陈启明',
      status: '已提交',
      createdAt: '10:05'
    }
  ],
  repairOrders: [
    {
      id: 'WO-20260626-019',
      title: '主轴振动值超过预警阈值',
      device: '五轴加工中心',
      priority: '高',
      assignee: '王工',
      createdAt: '08:42',
      status: '处理中'
    },
    {
      id: 'WO-20260626-020',
      title: '扫码枪间歇性断连',
      device: '自动化装配线',
      priority: '中',
      assignee: '刘工',
      createdAt: '10:15',
      status: '待派工'
    },
    {
      id: 'WO-20260625-087',
      title: '冷却液液位传感器需校准',
      device: '激光切割机',
      priority: '低',
      assignee: '赵工',
      createdAt: '昨天',
      status: '待验收'
    }
  ],
  weeklyUsage: [
    { name: '周一', value: 72 },
    { name: '周二', value: 79 },
    { name: '周三', value: 83 },
    { name: '周四', value: 77 },
    { name: '周五', value: 86 },
    { name: '周六', value: 69 },
    { name: '周日', value: 58 }
  ],
  orderTrend: [
    { name: '1月', value: 42 },
    { name: '2月', value: 51 },
    { name: '3月', value: 47 },
    { name: '4月', value: 62 },
    { name: '5月', value: 56 },
    { name: '6月', value: 71 }
  ],
  productionRecords: [
    { line: '精密制造一线', output: 1260, passRate: 98.4, oee: 82.1, energy: 2140 },
    { line: '自动化装配线', output: 1840, passRate: 96.8, oee: 79.3, energy: 1886 },
    { line: '钣金加工区', output: 920, passRate: 97.2, oee: 74.5, energy: 2435 },
    { line: '可靠性实验室', output: 138, passRate: 99.1, oee: 68.7, energy: 736 }
  ]
};
