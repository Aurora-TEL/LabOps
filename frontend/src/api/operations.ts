import { requestApi, type PageData } from '@/api/client';
import { workbenchData } from '@/mock/operations';
import type { DeviceStatus, Metric, ProductionRecord, RepairOrder, Reservation, WorkbenchData } from '@/types';

type BackendDeviceStatus = 'available' | 'reserved' | 'in_use' | 'maintenance' | 'disabled';
type BackendReservationStatus = 'pending' | 'approved' | 'rejected' | 'canceled' | 'completed';
type BackendWorkOrderStatus = 'pending' | 'processing' | 'finished' | 'canceled';
type BackendPriority = 'low' | 'medium' | 'high' | 'urgent';

interface DashboardSummary {
  device_total: number;
  device_available: number;
  today_reservations: number;
  pending_repairs: number;
  open_work_orders: number;
}

interface TrendPoint {
  date: string;
  value: number;
}

interface BackendDevice {
  id: string;
  code: string;
  name: string;
  status: BackendDeviceStatus;
  health_score?: number | null;
  purchase_date?: string | null;
}

interface BackendReservation {
  id: string;
  device_id: string;
  applicant_id: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: BackendReservationStatus;
}

interface BackendWorkOrder {
  id: string;
  repair_report_id: string;
  assignee_id?: string | null;
  priority: BackendPriority;
  status: BackendWorkOrderStatus;
  created_at: string;
}

const deviceStatusMap: Record<BackendDeviceStatus, DeviceStatus['status']> = {
  available: '待机',
  reserved: '待机',
  in_use: '运行中',
  maintenance: '维护中',
  disabled: '离线'
};

const reservationStatusMap: Record<BackendReservationStatus, Reservation['status']> = {
  pending: '待审核',
  approved: '已确认',
  rejected: '已完成',
  canceled: '已完成',
  completed: '已完成'
};

const workOrderStatusMap: Record<BackendWorkOrderStatus, RepairOrder['status']> = {
  pending: '待派工',
  processing: '处理中',
  finished: '待验收',
  canceled: '已关闭'
};

const priorityMap: Record<BackendPriority, RepairOrder['priority']> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '高'
};

export interface WorkbenchLoadResult {
  data: WorkbenchData;
  source: 'api' | 'mock';
  error?: string;
}

function formatDateLabel(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

function formatTimeRange(start: string, end: string) {
  const startDate = new Date(start);
  const endDate = new Date(end);

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return '待排程';
  }

  return `${startDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}-${endDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
}

function formatCreatedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function buildMetrics(summary: DashboardSummary): Metric[] {
  const total = Math.max(summary.device_total, 1);
  const availability = ((summary.device_available / total) * 100).toFixed(1);

  return [
    { label: '设备可用率', value: availability, unit: '%', trend: 'up', delta: `${summary.device_available}/${summary.device_total}`, accent: 'blue' },
    { label: '今日预约', value: String(summary.today_reservations), unit: '单', trend: 'flat', delta: '实时同步', accent: 'orange' },
    { label: '待处理报修', value: String(summary.pending_repairs), unit: '项', trend: summary.pending_repairs > 0 ? 'up' : 'flat', delta: '待闭环', accent: 'violet' },
    { label: '打开工单', value: String(summary.open_work_orders), unit: '张', trend: 'flat', delta: '处理中', accent: 'green' }
  ];
}

function mapDevice(item: BackendDevice, index: number): DeviceStatus {
  const mock = workbenchData.deviceStatuses[index % workbenchData.deviceStatuses.length];
  const healthScore = item.health_score ?? mock.utilization;

  return {
    id: item.code || item.id.slice(0, 8),
    name: item.name,
    workshop: mock.workshop,
    status: deviceStatusMap[item.status] ?? '待机',
    utilization: Math.round(healthScore),
    temperature: mock.temperature,
    nextMaintenance: item.purchase_date ?? mock.nextMaintenance
  };
}

function mapReservation(item: BackendReservation, index: number, devices: DeviceStatus[]): Reservation {
  const mock = workbenchData.reservations[index % workbenchData.reservations.length];
  const device = devices.find((candidate) => item.device_id.includes(candidate.id) || candidate.id.includes(item.device_id.slice(0, 8)));

  return {
    id: `RSV-${item.id.slice(0, 8)}`,
    device: device?.name ?? mock.device,
    applicant: `用户 ${item.applicant_id.slice(0, 4)}`,
    department: mock.department,
    slot: formatTimeRange(item.start_time, item.end_time),
    status: reservationStatusMap[item.status] ?? '待审核'
  };
}

function mapWorkOrder(item: BackendWorkOrder, index: number, devices: DeviceStatus[]): RepairOrder {
  const mock = workbenchData.repairOrders[index % workbenchData.repairOrders.length];
  const device = devices[index % Math.max(devices.length, 1)];

  return {
    id: `WO-${item.id.slice(0, 8)}`,
    title: mock.title,
    device: device?.name ?? mock.device,
    priority: priorityMap[item.priority] ?? '中',
    assignee: item.assignee_id ? `工程师 ${item.assignee_id.slice(0, 4)}` : '待派工',
    createdAt: formatCreatedAt(item.created_at),
    status: workOrderStatusMap[item.status] ?? '待派工'
  };
}

function mapProductionRecords(devices: DeviceStatus[]): ProductionRecord[] {
  if (devices.length === 0) return workbenchData.productionRecords;

  return devices.slice(0, 4).map((device, index) => {
    const mock = workbenchData.productionRecords[index % workbenchData.productionRecords.length];
    return {
      line: device.workshop,
      output: mock.output,
      passRate: mock.passRate,
      oee: Math.max(50, Math.min(99, device.utilization - 4)),
      energy: mock.energy
    };
  });
}

async function loadApiWorkbenchData(): Promise<WorkbenchData> {
  const [summary, utilization, repairTrend, devicesPage, reservationsPage, workOrdersPage] = await Promise.all([
    requestApi<DashboardSummary>('/dashboard/summary'),
    requestApi<TrendPoint[]>('/dashboard/device-utilization'),
    requestApi<TrendPoint[]>('/dashboard/repair-trend'),
    requestApi<PageData<BackendDevice>>('/devices?page_size=20'),
    requestApi<PageData<BackendReservation>>('/reservations?page_size=20'),
    requestApi<PageData<BackendWorkOrder>>('/work-orders?page_size=20')
  ]);

  const deviceStatuses = devicesPage.items.map(mapDevice);
  const reservations = reservationsPage.items.map((item, index) => mapReservation(item, index, deviceStatuses));
  const repairOrders = workOrdersPage.items.map((item, index) => mapWorkOrder(item, index, deviceStatuses));

  return {
    metrics: buildMetrics(summary),
    deviceStatuses,
    reservations,
    repairOrders,
    weeklyUsage: utilization.map((item) => ({ name: formatDateLabel(item.date), value: Math.round(item.value) })),
    orderTrend: repairTrend.map((item) => ({ name: formatDateLabel(item.date), value: Math.round(item.value) })),
    productionRecords: mapProductionRecords(deviceStatuses)
  };
}

export async function getWorkbenchData(): Promise<WorkbenchLoadResult> {
  try {
    return {
      data: await loadApiWorkbenchData(),
      source: 'api'
    };
  } catch (error) {
    return {
      data: workbenchData,
      source: 'mock',
      error: error instanceof Error ? error.message : '后端接口暂不可用，已切换演示数据'
    };
  }
}
