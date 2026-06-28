import { requestApi, type PageData } from '@/api/client';
import { workbenchData } from '@/mock/operations';
import type {
  DeviceStatus,
  MaintenanceRecord,
  Metric,
  ProductionRecord,
  RepairOrder,
  RepairReport,
  Reservation,
  ReservationAvailability,
  ReservationCalendarItem,
  WorkbenchData
} from '@/types';

export type BackendDeviceStatus = 'available' | 'reserved' | 'in_use' | 'maintenance' | 'disabled';
export type BackendReservationStatus = 'pending' | 'approved' | 'rejected' | 'canceled' | 'completed';
export type BackendRepairReportStatus = 'submitted' | 'accepted' | 'assigned' | 'processing' | 'finished' | 'closed';
export type BackendWorkOrderStatus = 'pending' | 'assigned' | 'processing' | 'finished' | 'canceled' | 'closed';
export type BackendPriority = 'low' | 'medium' | 'high' | 'urgent';
export type BackendMaintenanceType = 'routine' | 'repair' | 'calibration' | 'replacement' | 'enable' | 'disable';

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

export interface BackendDevice {
  id: string;
  code: string;
  name: string;
  status: BackendDeviceStatus;
  health_score?: number | null;
  purchase_date?: string | null;
  manager_id?: string | null;
}

export interface BackendReservation {
  id: string;
  device_id: string;
  applicant_id: string;
  reservation_no?: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: BackendReservationStatus;
}

export interface BackendReservationCalendarItem {
  id: string;
  reservation_no: string;
  device_id: string;
  applicant_id: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: BackendReservationStatus;
  title: string;
}

export interface BackendReservationAvailability {
  device_id: string;
  start_time: string;
  end_time: string;
  available: boolean;
  conflict_count: number;
  conflicts: BackendReservationCalendarItem[];
}

export interface BackendRepairReport {
  id: string;
  device_id: string;
  reporter_id: string;
  fault_type: string;
  description: string;
  status: BackendRepairReportStatus;
  created_at: string;
}

export interface BackendWorkOrder {
  id: string;
  repair_report_id: string;
  assignee_id?: string | null;
  priority: BackendPriority;
  status: BackendWorkOrderStatus;
  created_at: string;
}

export interface BackendMaintenanceRecord {
  id: string;
  device_id: string;
  work_order_id?: string | null;
  maintenance_type: BackendMaintenanceType;
  title: string;
  content: string;
  result?: string | null;
  cost_amount?: string | null;
  maintained_at: string;
  next_maintenance_at?: string | null;
}

export interface CreateDevicePayload {
  code: string;
  name: string;
  status: BackendDeviceStatus;
  health_score?: number | null;
  purchase_date?: string | null;
}

export interface CreateReservationPayload {
  device_id: string;
  start_time: string;
  end_time: string;
  purpose: string;
}

export interface CreateRepairReportPayload {
  device_id: string;
  fault_type: string;
  description: string;
}

export interface CreateWorkOrderPayload {
  repair_report_id: string;
  priority: BackendPriority;
  assignee_id?: string | null;
}

export interface CreateMaintenanceRecordPayload {
  device_id: string;
  maintenance_type: BackendMaintenanceType;
  title: string;
  content: string;
  result?: string | null;
  maintained_at?: string | null;
  next_maintenance_at?: string | null;
}

export interface WorkbenchLoadResult {
  data: WorkbenchData;
  source: 'api' | 'mock';
  error?: string;
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

const repairReportStatusMap: Record<BackendRepairReportStatus, RepairReport['status']> = {
  submitted: '已提交',
  accepted: '已受理',
  assigned: '已派单',
  processing: '已派单',
  finished: '已派单',
  closed: '已关闭'
};

const workOrderStatusMap: Record<BackendWorkOrderStatus, RepairOrder['status']> = {
  pending: '待派工',
  assigned: '待派工',
  processing: '处理中',
  finished: '待验收',
  canceled: '已关闭',
  closed: '已关闭'
};

const priorityMap: Record<BackendPriority, RepairOrder['priority']> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '高'
};

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

function shortId(prefix: string, id: string) {
  return `${prefix}-${id.slice(0, 8)}`;
}

function findDeviceName(deviceId: string, devices: DeviceStatus[], fallback: string) {
  return devices.find((candidate) => candidate.rawId === deviceId || candidate.id === deviceId)?.name ?? fallback;
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

export function mapDevice(item: BackendDevice, index: number): DeviceStatus {
  const mock = workbenchData.deviceStatuses[index % workbenchData.deviceStatuses.length];
  const healthScore = item.health_score ?? mock.utilization;

  return {
    rawId: item.id,
    id: item.code || item.id.slice(0, 8),
    name: item.name,
    workshop: mock.workshop,
    status: deviceStatusMap[item.status] ?? '待机',
    utilization: Math.round(healthScore),
    temperature: mock.temperature,
    nextMaintenance: item.purchase_date ?? mock.nextMaintenance
  };
}

export function mapReservation(item: BackendReservation, index: number, devices: DeviceStatus[]): Reservation {
  const mock = workbenchData.reservations[index % workbenchData.reservations.length];

  return {
    rawId: item.id,
    rawDeviceId: item.device_id,
    id: item.reservation_no ?? shortId('RSV', item.id),
    device: findDeviceName(item.device_id, devices, mock.device),
    applicant: `用户 ${item.applicant_id.slice(0, 4)}`,
    department: mock.department,
    slot: formatTimeRange(item.start_time, item.end_time),
    startAt: item.start_time,
    endAt: item.end_time,
    purpose: item.purpose,
    status: reservationStatusMap[item.status] ?? '待审核'
  };
}

function mapCalendarItem(item: BackendReservationCalendarItem): ReservationCalendarItem {
  return {
    id: item.id,
    reservationNo: item.reservation_no,
    deviceId: item.device_id,
    applicantId: item.applicant_id,
    startTime: item.start_time,
    endTime: item.end_time,
    purpose: item.purpose,
    status: item.status,
    title: item.title
  };
}

function mapAvailability(item: BackendReservationAvailability): ReservationAvailability {
  return {
    deviceId: item.device_id,
    startTime: item.start_time,
    endTime: item.end_time,
    available: item.available,
    conflictCount: item.conflict_count,
    conflicts: item.conflicts.map(mapCalendarItem)
  };
}

export function mapRepairReport(item: BackendRepairReport, index: number, devices: DeviceStatus[]): RepairReport {
  const mock = workbenchData.repairReports[index % workbenchData.repairReports.length] ?? workbenchData.repairReports[0];

  return {
    rawId: item.id,
    rawDeviceId: item.device_id,
    id: shortId('REP', item.id),
    device: findDeviceName(item.device_id, devices, mock?.device ?? '未知设备'),
    faultType: item.fault_type,
    description: item.description,
    reporter: `用户 ${item.reporter_id.slice(0, 4)}`,
    status: repairReportStatusMap[item.status] ?? '已提交',
    createdAt: formatCreatedAt(item.created_at)
  };
}

export function mapWorkOrder(item: BackendWorkOrder, index: number, devices: DeviceStatus[], repairReports: RepairReport[]): RepairOrder {
  const mock = workbenchData.repairOrders[index % workbenchData.repairOrders.length];
  const report = repairReports.find((candidate) => candidate.rawId === item.repair_report_id);
  const device = report?.device ?? devices[index % Math.max(devices.length, 1)]?.name ?? mock.device;

  return {
    rawId: item.id,
    rawRepairReportId: item.repair_report_id,
    id: shortId('WO', item.id),
    title: report?.description ?? mock.title,
    device,
    priority: priorityMap[item.priority] ?? '中',
    assignee: item.assignee_id ? `工程师 ${item.assignee_id.slice(0, 4)}` : '待派工',
    createdAt: formatCreatedAt(item.created_at),
    status: workOrderStatusMap[item.status] ?? '待派工'
  };
}

export function mapMaintenanceRecord(item: BackendMaintenanceRecord): MaintenanceRecord {
  return {
    id: shortId('MTN', item.id),
    rawId: item.id,
    rawDeviceId: item.device_id,
    type: item.maintenance_type,
    title: item.title,
    content: item.content,
    result: item.result,
    costAmount: item.cost_amount,
    maintainedAt: item.maintained_at,
    nextMaintenanceAt: item.next_maintenance_at
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

async function maybeLoadWorkOrders(devices: DeviceStatus[], repairReports: RepairReport[]) {
  try {
    const workOrdersPage = await requestApi<PageData<BackendWorkOrder>>('/work-orders?page_size=20');
    return workOrdersPage.items.map((item, index) => mapWorkOrder(item, index, devices, repairReports));
  } catch {
    return [];
  }
}

async function loadApiWorkbenchData(): Promise<WorkbenchData> {
  const [summary, utilization, repairTrend, devicesPage, reservationsPage, repairReportsPage] = await Promise.all([
    requestApi<DashboardSummary>('/dashboard/summary'),
    requestApi<TrendPoint[]>('/dashboard/device-utilization'),
    requestApi<TrendPoint[]>('/dashboard/repair-trend'),
    requestApi<PageData<BackendDevice>>('/devices?page_size=20'),
    requestApi<PageData<BackendReservation>>('/reservations?page_size=20'),
    requestApi<PageData<BackendRepairReport>>('/repair-reports?page_size=20')
  ]);

  const deviceStatuses = devicesPage.items.map(mapDevice);
  const reservations = reservationsPage.items.map((item, index) => mapReservation(item, index, deviceStatuses));
  const repairReports = repairReportsPage.items.map((item, index) => mapRepairReport(item, index, deviceStatuses));
  const repairOrders = await maybeLoadWorkOrders(deviceStatuses, repairReports);

  return {
    metrics: buildMetrics(summary),
    deviceStatuses,
    reservations,
    repairReports,
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

export function createDevice(payload: CreateDevicePayload) {
  return requestApi<BackendDevice>('/devices', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export function updateDeviceStatus(deviceId: string, status: BackendDeviceStatus, reason: string) {
  return requestApi<BackendDevice>(`/devices/${deviceId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, reason })
  });
}

export function createReservation(payload: CreateReservationPayload) {
  return requestApi<BackendReservation>('/reservations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function getReservationCalendar(params: {
  start_time: string;
  end_time: string;
  device_id?: string;
}) {
  const search = new URLSearchParams({
    start_time: params.start_time,
    end_time: params.end_time
  });
  if (params.device_id) search.set('device_id', params.device_id);
  const items = await requestApi<BackendReservationCalendarItem[]>(`/reservations/calendar?${search.toString()}`);
  return items.map(mapCalendarItem);
}

export async function checkReservationAvailability(deviceId: string, startTime: string, endTime: string) {
  const search = new URLSearchParams({
    device_id: deviceId,
    start_time: startTime,
    end_time: endTime
  });
  return mapAvailability(await requestApi<BackendReservationAvailability>(`/reservations/availability?${search.toString()}`));
}

export function approveReservation(reservationId: string) {
  return requestApi<BackendReservation>(`/reservations/${reservationId}/approve`, { method: 'POST' });
}

export function rejectReservation(reservationId: string, rejectReason: string) {
  return requestApi<BackendReservation>(`/reservations/${reservationId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reject_reason: rejectReason })
  });
}

export function cancelReservation(reservationId: string) {
  return requestApi<BackendReservation>(`/reservations/${reservationId}/cancel`, { method: 'POST' });
}

export function createRepairReport(payload: CreateRepairReportPayload) {
  return requestApi<BackendRepairReport>('/repair-reports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export function createWorkOrder(payload: CreateWorkOrderPayload) {
  return requestApi<BackendWorkOrder>('/work-orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export function updateWorkOrderStatus(workOrderId: string, status: BackendWorkOrderStatus) {
  return requestApi<BackendWorkOrder>(`/work-orders/${workOrderId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
}

export function finishWorkOrder(workOrderId: string, result: string) {
  return requestApi<BackendWorkOrder>(`/work-orders/${workOrderId}/finish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result })
  });
}

export async function getMaintenanceRecords(deviceId: string) {
  const page = await requestApi<PageData<BackendMaintenanceRecord>>(
    `/maintenance-records?device_id=${encodeURIComponent(deviceId)}&page_size=20`
  );
  return page.items.map(mapMaintenanceRecord);
}

export function createMaintenanceRecord(payload: CreateMaintenanceRecordPayload) {
  return requestApi<BackendMaintenanceRecord>('/maintenance-records', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}
