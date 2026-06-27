import { defineStore } from 'pinia';

import {
  approveReservation,
  cancelReservation,
  createDevice,
  createRepairReport,
  createReservation,
  createWorkOrder,
  finishWorkOrder,
  getWorkbenchData,
  rejectReservation,
  updateDeviceStatus,
  updateWorkOrderStatus,
  type BackendDeviceStatus,
  type BackendPriority,
  type BackendWorkOrderStatus,
  type CreateDevicePayload,
  type CreateRepairReportPayload,
  type CreateReservationPayload,
  type CreateWorkOrderPayload
} from '@/api/operations';
import { workbenchData } from '@/mock/operations';
import type { DeviceStatus, RepairOrder, RepairReport, Reservation, WorkbenchData } from '@/types';

const deviceStatusLabel: Record<BackendDeviceStatus, DeviceStatus['status']> = {
  available: '待机',
  reserved: '待机',
  in_use: '运行中',
  maintenance: '维护中',
  disabled: '离线'
};

const workOrderStatusLabel: Record<BackendWorkOrderStatus, RepairOrder['status']> = {
  pending: '待派工',
  processing: '处理中',
  finished: '待验收',
  canceled: '已关闭'
};

const priorityLabel: Record<BackendPriority, RepairOrder['priority']> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '高'
};

function demoId(prefix: string) {
  return `${prefix}-${new Date().toISOString().replace(/\D/g, '').slice(2, 12)}`;
}

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

export const useOperationsStore = defineStore('operations', {
  state: () => ({
    data: workbenchData as WorkbenchData,
    loading: false,
    actionLoading: '',
    error: '',
    success: '',
    source: 'mock' as 'api' | 'mock',
    loaded: false
  }),
  actions: {
    async load() {
      this.loading = true;
      try {
        const result = await getWorkbenchData();
        this.data = result.data;
        this.source = result.source;
        this.error = result.error ?? '';
        this.loaded = true;
      } finally {
        this.loading = false;
      }
    },
    async refresh() {
      this.success = '';
      await this.load();
    },
    beginAction(name: string) {
      this.actionLoading = name;
      this.error = '';
      this.success = '';
    },
    endAction() {
      this.actionLoading = '';
    },
    markFallback(error: unknown, message: string) {
      this.source = 'mock';
      this.error = error instanceof Error ? `${error.message}，已使用演示数据完成操作` : '后端接口暂不可用，已使用演示数据完成操作';
      this.success = message;
    },
    async createDevice(payload: CreateDevicePayload) {
      this.beginAction('device:create');
      try {
        await createDevice(payload);
        this.success = '设备已创建，列表已刷新';
        await this.load();
      } catch (error) {
        this.data.deviceStatuses.unshift({
          rawId: demoId('demo-device'),
          id: payload.code,
          name: payload.name,
          workshop: '演示实验室',
          status: deviceStatusLabel[payload.status],
          utilization: Math.round(payload.health_score ?? 80),
          temperature: 36,
          nextMaintenance: payload.purchase_date ?? '待维护'
        });
        this.markFallback(error, '设备已加入演示列表');
      } finally {
        this.endAction();
      }
    },
    async setDeviceStatus(device: DeviceStatus, status: BackendDeviceStatus) {
      this.beginAction(`device:${device.id}`);
      try {
        await updateDeviceStatus(device.rawId ?? device.id, status, '前端演示操作');
        this.success = '设备状态已更新';
        await this.load();
      } catch (error) {
        device.status = deviceStatusLabel[status];
        this.markFallback(error, '设备状态已在演示数据中更新');
      } finally {
        this.endAction();
      }
    },
    async createReservation(payload: CreateReservationPayload) {
      this.beginAction('reservation:create');
      try {
        await createReservation(payload);
        this.success = '预约已提交，列表已刷新';
        await this.load();
      } catch (error) {
        const device = this.data.deviceStatuses.find((item) => item.rawId === payload.device_id || item.id === payload.device_id);
        this.data.reservations.unshift({
          rawId: demoId('demo-reservation'),
          rawDeviceId: payload.device_id,
          id: demoId('RSV'),
          device: device?.name ?? '演示设备',
          applicant: '当前用户',
          department: '演示部门',
          slot: `${formatTime(payload.start_time)}-${formatTime(payload.end_time)}`,
          status: '待审核'
        });
        this.markFallback(error, '预约已加入演示列表');
      } finally {
        this.endAction();
      }
    },
    async changeReservationStatus(reservation: Reservation, action: 'approve' | 'reject' | 'cancel') {
      this.beginAction(`reservation:${reservation.id}:${action}`);
      try {
        if (action === 'approve') await approveReservation(reservation.rawId ?? reservation.id);
        if (action === 'reject') await rejectReservation(reservation.rawId ?? reservation.id, '演示拒绝：该时段资源调整');
        if (action === 'cancel') await cancelReservation(reservation.rawId ?? reservation.id);
        this.success = '预约状态已更新';
        await this.load();
      } catch (error) {
        reservation.status = action === 'approve' ? '已确认' : '已完成';
        this.markFallback(error, '预约状态已在演示数据中更新');
      } finally {
        this.endAction();
      }
    },
    async createRepairReport(payload: CreateRepairReportPayload) {
      this.beginAction('repair:create');
      try {
        await createRepairReport(payload);
        this.success = '报修已提交，列表已刷新';
        await this.load();
      } catch (error) {
        const device = this.data.deviceStatuses.find((item) => item.rawId === payload.device_id || item.id === payload.device_id);
        this.data.repairReports.unshift({
          rawId: demoId('demo-report'),
          rawDeviceId: payload.device_id,
          id: demoId('REP'),
          device: device?.name ?? '演示设备',
          faultType: payload.fault_type,
          description: payload.description,
          reporter: '当前用户',
          status: '已提交',
          createdAt: formatTime(new Date().toISOString())
        });
        this.markFallback(error, '报修已加入演示列表');
      } finally {
        this.endAction();
      }
    },
    async createWorkOrder(payload: CreateWorkOrderPayload) {
      this.beginAction('work-order:create');
      try {
        await createWorkOrder(payload);
        this.success = '工单已创建，列表已刷新';
        await this.load();
      } catch (error) {
        const report = this.data.repairReports.find((item) => item.rawId === payload.repair_report_id || item.id === payload.repair_report_id);
        if (report) report.status = '已派单';
        this.data.repairOrders.unshift({
          rawId: demoId('demo-work-order'),
          rawRepairReportId: payload.repair_report_id,
          id: demoId('WO'),
          title: report?.description ?? '演示工单',
          device: report?.device ?? '演示设备',
          priority: priorityLabel[payload.priority],
          assignee: payload.assignee_id ? `工程师 ${payload.assignee_id.slice(0, 4)}` : '待派工',
          createdAt: formatTime(new Date().toISOString()),
          status: '待派工'
        });
        this.markFallback(error, '工单已加入演示看板');
      } finally {
        this.endAction();
      }
    },
    async changeWorkOrderStatus(order: RepairOrder, status: BackendWorkOrderStatus) {
      this.beginAction(`work-order:${order.id}:${status}`);
      try {
        if (status === 'finished') {
          await finishWorkOrder(order.rawId ?? order.id, '演示处理完成，待业务验收');
        } else {
          await updateWorkOrderStatus(order.rawId ?? order.id, status);
        }
        this.success = '工单状态已更新';
        await this.load();
      } catch (error) {
        order.status = workOrderStatusLabel[status];
        if (status === 'finished') {
          const report = this.data.repairReports.find((item) => item.rawId === order.rawRepairReportId);
          if (report) report.status = '已关闭';
        }
        this.markFallback(error, '工单状态已在演示数据中更新');
      } finally {
        this.endAction();
      }
    }
  }
});
