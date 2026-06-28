import type { AnalyticsReport } from '@/types';

export const analyticsReport: AnalyticsReport = {
  startDate: '2026-06-01',
  endDate: '2026-06-30',
  kpis: [
    { label: '设备平均健康分', value: 86.7, unit: '分', delta: '9 台设备', status: 'normal' },
    { label: '预约占用时长', value: 128.5, unit: '小时', delta: '42 单已确认', status: 'normal' },
    { label: '估算利用率', value: 71.4, unit: '%', delta: '30 天窗口', status: 'normal' },
    { label: '平均维修时长', value: 12.8, unit: '小时', delta: '8 单已关闭', status: 'warning' },
    { label: '工单闭环率', value: 82.6, unit: '%', delta: '19/23', status: 'normal' }
  ],
  reservationTrend: [
    { date: '2026-06-24', value: 5 },
    { date: '2026-06-25', value: 7 },
    { date: '2026-06-26', value: 6 },
    { date: '2026-06-27', value: 9 },
    { date: '2026-06-28', value: 8 },
    { date: '2026-06-29', value: 11 },
    { date: '2026-06-30', value: 10 }
  ],
  repairTrend: [
    { date: '2026-06-24', value: 2 },
    { date: '2026-06-25', value: 3 },
    { date: '2026-06-26', value: 1 },
    { date: '2026-06-27', value: 4 },
    { date: '2026-06-28', value: 2 },
    { date: '2026-06-29', value: 5 },
    { date: '2026-06-30', value: 3 }
  ],
  reservationStatus: [
    { status: 'pending', count: 8 },
    { status: 'approved', count: 42 },
    { status: 'completed', count: 31 },
    { status: 'rejected', count: 3 },
    { status: 'canceled', count: 2 }
  ],
  faultTypes: [
    { name: 'hardware', count: 7 },
    { name: 'software', count: 5 },
    { name: 'network', count: 4 },
    { name: 'calibration', count: 3 }
  ],
  maintenanceTypes: [
    { name: 'routine', count: 12 },
    { name: 'repair', count: 8 },
    { name: 'calibration', count: 6 },
    { name: 'replacement', count: 3 }
  ],
  deviceHealth: [
    { deviceId: 'DEV-3DP-A01', deviceName: '3D Printer A01', status: 'available', healthScore: 92 },
    { deviceId: 'DEV-LAS-L01', deviceName: 'Laser Cutter L01', status: 'in_use', healthScore: 85 },
    { deviceId: 'DEV-IOT-GW01', deviceName: 'IoT Gateway GW01', status: 'available', healthScore: 78 },
    { deviceId: 'DEV-NET-01', deviceName: 'Network Analyzer NET-01', status: 'maintenance', healthScore: 64 }
  ]
};
