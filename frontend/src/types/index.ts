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
  rawId?: string;
  id: string;
  name: string;
  workshop: string;
  status: '运行中' | '待机' | '维护中' | '离线';
  utilization: number;
  temperature: number;
  nextMaintenance: string;
}

export interface Reservation {
  rawId?: string;
  rawDeviceId?: string;
  id: string;
  device: string;
  applicant: string;
  department: string;
  slot: string;
  status: '待审核' | '已确认' | '进行中' | '已完成';
}

export interface RepairOrder {
  rawId?: string;
  rawRepairReportId?: string;
  id: string;
  title: string;
  device: string;
  priority: '高' | '中' | '低';
  assignee: string;
  createdAt: string;
  status: '待派工' | '处理中' | '待验收' | '已关闭';
}

export interface RepairReport {
  rawId?: string;
  rawDeviceId?: string;
  id: string;
  device: string;
  faultType: string;
  description: string;
  reporter: string;
  status: '已提交' | '已受理' | '已派单' | '已关闭';
  createdAt: string;
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
  repairReports: RepairReport[];
  repairOrders: RepairOrder[];
  weeklyUsage: ChartPoint[];
  orderTrend: ChartPoint[];
  productionRecords: ProductionRecord[];
}

export type NotificationType = 'reservation' | 'repair' | 'work_order' | 'system';

export interface NotificationItem {
  id: string;
  title: string;
  content: string;
  type: NotificationType;
  createdAt: string;
  read: boolean;
  link?: string;
}

export interface RecentOperation {
  id: string;
  actor: string;
  action: string;
  target: string;
  detail: string;
  createdAt: string;
  status: 'success' | 'warning' | 'failed';
}

export interface NotificationCenterData {
  notifications: NotificationItem[];
  recentOperations: RecentOperation[];
}
