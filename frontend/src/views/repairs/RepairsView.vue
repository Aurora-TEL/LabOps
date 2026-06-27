<script setup lang="ts">
import { ClipboardPlus, Plus, RefreshCw } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, reactive, ref } from 'vue';

import type { BackendPriority } from '@/api/operations';
import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);
const showRepairForm = ref(false);
const showWorkOrderForm = ref(false);
const repairForm = reactive({
  device_id: '',
  fault_type: 'hardware',
  description: '设备运行异常，请安排检查'
});
const workOrderForm = reactive({
  repair_report_id: '',
  priority: 'medium' as BackendPriority
});

const columns = ['待派工', '处理中', '待验收', '已关闭'];
const groupedOrders = computed(() =>
  columns.map((status) => ({
    status,
    items: data.value.repairOrders.filter((item) => item.status === status)
  }))
);

function firstDeviceId() {
  return data.value.deviceStatuses[0]?.rawId || data.value.deviceStatuses[0]?.id || '';
}

function firstReportId() {
  return data.value.repairReports[0]?.rawId || data.value.repairReports[0]?.id || '';
}

async function submitRepair() {
  await store.createRepairReport({
    device_id: repairForm.device_id || firstDeviceId(),
    fault_type: repairForm.fault_type,
    description: repairForm.description
  });
  showRepairForm.value = false;
}

async function submitWorkOrder() {
  await store.createWorkOrder({
    repair_report_id: workOrderForm.repair_report_id || firstReportId(),
    priority: workOrderForm.priority
  });
  showWorkOrderForm.value = false;
}
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">运维闭环</p>
        <h1>报修工单看板</h1>
        <p class="subtle">按照报修、派工、处理、验收到关闭的流程呈现，方便答辩演示运维闭环。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <button class="text-button" type="button" :disabled="loading" @click="store.refresh"><RefreshCw :size="17" />刷新</button>
        <button class="text-button" type="button" @click="showWorkOrderForm = !showWorkOrderForm"><Plus :size="17" />创建工单</button>
        <button class="text-button primary" type="button" @click="showRepairForm = !showRepairForm"><ClipboardPlus :size="17" />提交报修</button>
      </div>
    </section>

    <section v-if="showRepairForm" class="panel">
      <form class="inline-form compact" @submit.prevent="submitRepair">
        <label class="form-item">
          故障设备
          <select v-model="repairForm.device_id" required>
            <option disabled value="">请选择设备</option>
            <option v-for="device in data.deviceStatuses" :key="device.id" :value="device.rawId ?? device.id">{{ device.name }}</option>
          </select>
        </label>
        <label class="form-item">
          故障类型
          <select v-model="repairForm.fault_type">
            <option value="hardware">硬件</option>
            <option value="software">软件</option>
            <option value="network">网络</option>
            <option value="calibration">校准</option>
          </select>
        </label>
        <label class="form-item description">故障描述<textarea v-model.trim="repairForm.description" required rows="2" /></label>
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'repair:create'">
          {{ actionLoading === 'repair:create' ? '提交中' : '提交' }}
        </button>
      </form>
    </section>

    <section v-if="showWorkOrderForm" class="panel">
      <form class="inline-form compact" @submit.prevent="submitWorkOrder">
        <label class="form-item">
          关联报修
          <select v-model="workOrderForm.repair_report_id" required>
            <option disabled value="">请选择报修</option>
            <option v-for="report in data.repairReports" :key="report.id" :value="report.rawId ?? report.id">{{ report.id }} · {{ report.device }}</option>
          </select>
        </label>
        <label class="form-item">
          优先级
          <select v-model="workOrderForm.priority">
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
            <option value="urgent">紧急</option>
          </select>
        </label>
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'work-order:create' || data.repairReports.length === 0">
          {{ actionLoading === 'work-order:create' ? '创建中' : '创建' }}
        </button>
      </form>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading" :error="error" :empty="data.repairOrders.length === 0 && data.repairReports.length === 0" empty-text="暂无报修工单" />

    <section class="panel">
      <div class="panel-header">
        <h2>报修记录</h2>
        <span class="count">{{ data.repairReports.length }} 条</span>
      </div>
      <div class="panel-body table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>报修单</th>
              <th>设备</th>
              <th>类型</th>
              <th>描述</th>
              <th>报修人</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in data.repairReports" :key="report.id">
              <td class="strong">{{ report.id }}</td>
              <td>{{ report.device }}</td>
              <td>{{ report.faultType }}</td>
              <td>{{ report.description }}</td>
              <td>{{ report.reporter }}</td>
              <td><StatusPill :value="report.status" /></td>
            </tr>
            <tr v-if="data.repairReports.length === 0">
              <td colspan="6">暂无报修记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="kanban">
      <div v-for="column in groupedOrders" :key="column.status" class="panel lane">
        <div class="lane-header">
          <h2>{{ column.status }}</h2>
          <span>{{ column.items.length }}</span>
        </div>
        <article v-for="item in column.items" :key="item.id" class="ticket">
          <div class="ticket-top">
            <StatusPill :value="item.priority" />
            <span>{{ item.createdAt }}</span>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.device }}</p>
          <footer>
            <strong>{{ item.assignee }}</strong>
            <span>{{ item.id }}</span>
          </footer>
          <div class="row-actions">
            <button class="mini-button" type="button" :disabled="item.status !== '待派工' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(item, 'processing')">开始处理</button>
            <button class="mini-button primary" type="button" :disabled="item.status !== '处理中' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(item, 'finished')">完成</button>
            <button class="mini-button" type="button" :disabled="item.status === '已关闭' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(item, 'canceled')">关闭</button>
          </div>
        </article>
        <div v-if="column.items.length === 0" class="empty">暂无工单</div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.kanban {
  display: grid;
  grid-template-columns: repeat(4, minmax(220px, 1fr));
  gap: 16px;
  overflow-x: auto;
}

.lane {
  min-height: 430px;
  padding: 14px;
}

.lane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.lane-header span,
.count {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.lane-header span {
  display: inline-flex;
  min-width: 28px;
  height: 28px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  color: var(--blue);
  background: #e8f1ff;
  font-weight: 900;
}

.ticket {
  border: 1px solid #e4edf7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.ticket + .ticket,
.empty {
  margin-top: 12px;
}

.ticket-top,
.ticket footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.ticket-top span,
.ticket p,
.ticket footer span {
  color: var(--muted);
  font-size: 13px;
}

.ticket h3 {
  margin-top: 14px;
  line-height: 1.5;
}

.ticket p {
  margin-bottom: 16px;
}

.ticket footer strong {
  color: #172033;
}

.ticket .row-actions {
  margin-top: 14px;
}

.empty {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: center;
  border: 1px dashed #cfdceb;
  border-radius: 8px;
  color: var(--muted);
  background: #f8fbff;
  font-weight: 800;
}
</style>
