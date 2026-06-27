import type { WorkbenchData } from '@/types';

export const workbenchData: WorkbenchData = {
  metrics: [
    { label: '设备可用率', value: '86.4', unit: '%', trend: 'up', delta: '+4.8%', accent: 'blue' },
    { label: '待审核预约', value: '18', unit: '单', trend: 'down', delta: '-6', accent: 'orange' },
    { label: '处理中工单', value: '27', unit: '项', trend: 'up', delta: '+3', accent: 'violet' },
    { label: '综合 OEE', value: '78.9', unit: '%', trend: 'flat', delta: '持平', accent: 'green' }
  ],
  deviceStatuses: [
    {
      id: 'DEV-3DP-A01',
      name: '3D Printer A01',
      workshop: '智能制造实验室',
      status: '待机',
      utilization: 91,
      temperature: 42,
      nextMaintenance: '2026-07-03'
    },
    {
      id: 'DEV-LAS-L01',
      name: 'Laser Cutter L01',
      workshop: '智能制造实验室',
      status: '运行中',
      utilization: 84,
      temperature: 48,
      nextMaintenance: '2026-07-12'
    },
    {
      id: 'DEV-NET-01',
      name: 'Network Analyzer NET-01',
      workshop: '电子信息实验室',
      status: '维护中',
      utilization: 38,
      temperature: 29,
      nextMaintenance: '2026-06-28'
    },
    {
      id: 'DEV-IOT-GW01',
      name: 'IoT Gateway GW01',
      workshop: '传感与物联网实验室',
      status: '待机',
      utilization: 76,
      temperature: 36,
      nextMaintenance: '2026-07-08'
    }
  ],
  reservations: [
    {
      id: 'RSV-240621',
      device: '3D Printer A01',
      applicant: '当前用户',
      department: '机械工程学院',
      slot: '09:00-11:30',
      status: '已确认'
    },
    {
      id: 'RSV-240622',
      device: 'Laser Cutter L01',
      applicant: '当前用户',
      department: '机械工程学院',
      slot: '13:30-15:00',
      status: '待审核'
    },
    {
      id: 'RSV-240623',
      device: 'Network Analyzer NET-01',
      applicant: '用户 1024',
      department: '电子信息学院',
      slot: '15:30-18:00',
      status: '已完成'
    }
  ],
  repairReports: [
    {
      id: 'REP-20260626-014',
      device: 'Laser Cutter L01',
      faultType: 'mechanical',
      description: '激光头定位偏移，切割轨迹不稳定',
      reporter: '当前用户',
      status: '已派单',
      createdAt: '08:20'
    },
    {
      id: 'REP-20260626-015',
      device: 'Network Analyzer NET-01',
      faultType: 'network',
      description: '设备采集链路间歇性断开，影响实验记录',
      reporter: '用户 1024',
      status: '已提交',
      createdAt: '10:05'
    }
  ],
  repairOrders: [
    {
      id: 'WO-20260626-019',
      title: '激光头定位偏移，切割轨迹不稳定',
      device: 'Laser Cutter L01',
      priority: '高',
      assignee: 'Device Owner Demo',
      createdAt: '08:42',
      status: '处理中'
    },
    {
      id: 'WO-20260626-020',
      title: '设备采集链路间歇性断开',
      device: 'Network Analyzer NET-01',
      priority: '中',
      assignee: 'Lab Admin Demo',
      createdAt: '10:15',
      status: '待派工'
    },
    {
      id: 'WO-20260625-087',
      title: '3D 打印平台需要校准',
      device: '3D Printer A01',
      priority: '低',
      assignee: 'Device Owner Demo',
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
    { line: '智能制造实验室', output: 1260, passRate: 98.4, oee: 82.1, energy: 2140 },
    { line: '电子信息实验室', output: 1840, passRate: 96.8, oee: 79.3, energy: 1886 },
    { line: '传感与物联网实验室', output: 920, passRate: 97.2, oee: 74.5, energy: 2435 },
    { line: '可靠性测试室', output: 138, passRate: 99.1, oee: 68.7, energy: 736 }
  ]
};
