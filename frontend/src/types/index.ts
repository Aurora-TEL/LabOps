export type Trend = 'up' | 'down' | 'flat';

export interface Metric {
  label: string;
  value: string;
  unit: string;
  trend: Trend;
  delta: string;
  accent: 'blue' | 'green' | 'orange' | 'violet';
}

export interface DeviceStatus {
  id: string;
  name: string;
  workshop: string;
  status: '运行中' | '待机' | '维护中' | '离线';
  utilization: number;
  temperature: number;
  nextMaintenance: string;
}

export interface Reservation {
  id: string;
  device: string;
  applicant: string;
  department: string;
  slot: string;
  status: '待审核' | '已确认' | '进行中' | '已完成';
}

export interface RepairOrder {
  id: string;
  title: string;
  device: string;
  priority: '高' | '中' | '低';
  assignee: string;
  createdAt: string;
  status: '待派工' | '处理中' | '待验收' | '已关闭';
}

export interface ChartPoint {
  name: string;
  value: number;
}

export interface ProductionRecord {
  line: string;
  output: number;
  passRate: number;
  oee: number;
  energy: number;
}

export interface WorkbenchData {
  metrics: Metric[];
  deviceStatuses: DeviceStatus[];
  reservations: Reservation[];
  repairOrders: RepairOrder[];
  weeklyUsage: ChartPoint[];
  orderTrend: ChartPoint[];
  productionRecords: ProductionRecord[];
}
