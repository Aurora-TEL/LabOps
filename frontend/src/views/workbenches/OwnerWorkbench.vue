<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { Activity, Check, ClipboardPlus, RefreshCw, Wrench, X } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, reactive, ref } from 'vue';

import ChartPanel from '@/components/common/ChartPanel.vue';
import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import type { BackendPriority } from '@/api/operations';
import { useOperationsStore } from '@/stores/operations';

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);

const showWorkOrderForm = ref(false);
const workOrderForm = reactive({
  repair_report_id: '',
  priority: 'medium' as BackendPriority
});

const pendingReservations = computed(() => data.value.reservations.filter((item) => item.status === '待审核'));
const activeOrders = computed(() => data.value.repairOrders.filter((item) => item.status !== '已关闭'));
const pendingReports = computed(() => data.value.repairReports.filter((item) => item.status !== '已关闭'));
const ownerDevices = computed(() => data.value.deviceStatuses);

const utilizationOption = computed<EChartsOption>(() => ({
  color: ['#1769e0'],
  tooltip: { trigger: 'axis' },
  grid: { left: 36, right: 18, top: 28, bottom: 32 },
  xAxis: { type: 'category', data: data.value.weeklyUsage.map((item) => item.name), axisTick: { show: false } },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [{ type: 'line', smooth: true, symbolSize: 8, areaStyle: { opacity: 0.12 }, data: data.value.weeklyUsage.map((item) => item.value) }]
}));

const repairOption = computed<EChartsOption>(() => ({
  color: ['#00a6c8'],
  tooltip: { trigger: 'axis' },
  grid: { left: 36, right: 18, top: 28, bottom: 32 },
  xAxis: { type: 'category', data: data.value.orderTrend.map((item) => item.name), axisTick: { show: false } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [{ type: 'bar', barWidth: 24, data: data.value.orderTrend.map((item) => item.value), itemStyle: { borderRadius: [6, 6, 0, 0] } }]
}));

function firstReportId() {
  return pendingReports.value[0]?.rawId || pendingReports.value[0]?.id || '';
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
        <p class="eyebrow">设备负责人工作台</p>
        <h1>负责设备的预约审批与运维闭环</h1>
        <p class="subtle">聚焦本人负责设备，处理预约审核、故障报修、派工维修和状态维护。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <button class="text-button" type="button" :disabled="loading" @click="store.refresh"><RefreshCw :size="17" />刷新</button>
        <button class="text-button primary" type="button" @click="showWorkOrderForm = !showWorkOrderForm"><ClipboardPlus :size="17" />创建工单</button>
      </div>
    </section>

    <section class="grid metrics">
      <div class="panel owner-metric">
        <Wrench :size="22" />
        <strong>{{ ownerDevices.length }}</strong>
        <span>负责设备</span>
      </div>
      <div class="panel owner-metric">
        <Activity :size="22" />
        <strong>{{ pendingReservations.length }}</strong>
        <span>待审批预约</span>
      </div>
      <div class="panel owner-metric">
        <ClipboardPlus :size="22" />
        <strong>{{ pendingReports.length }}</strong>
        <span>待处理报修</span>
      </div>
      <div class="panel owner-metric">
        <Check :size="22" />
        <strong>{{ activeOrders.length }}</strong>
        <span>打开工单</span>
      </div>
    </section>

    <section v-if="showWorkOrderForm" class="panel">
      <form class="inline-form compact" @submit.prevent="submitWorkOrder">
        <label class="form-item">
          关联报修
          <select v-model="workOrderForm.repair_report_id" required>
            <option disabled value="">请选择报修</option>
            <option v-for="report in pendingReports" :key="report.id" :value="report.rawId ?? report.id">{{ report.id }} / {{ report.device }}</option>
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
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'work-order:create' || pendingReports.length === 0">
          {{ actionLoading === 'work-order:create' ? '创建中' : '创建工单' }}
        </button>
      </form>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading" :error="error" :empty="ownerDevices.length === 0" empty-text="暂无负责设备" />

    <section class="grid two">
      <ChartPanel title="负责设备健康度" :option="utilizationOption">
        <template #extra><span class="chart-note"><Activity :size="16" />按负责人范围</span></template>
      </ChartPanel>
      <ChartPanel title="负责设备报修趋势" :option="repairOption">
        <template #extra><span class="chart-note"><Wrench :size="16" />维修闭环</span></template>
      </ChartPanel>
    </section>

    <section class="grid two">
      <div class="panel">
        <div class="panel-header">
          <h2>负责设备状态</h2>
          <span class="count">{{ ownerDevices.length }} 台</span>
        </div>
        <div class="panel-body device-list">
          <article v-for="device in ownerDevices" :key="device.id" class="device-row">
            <div>
              <strong>{{ device.name }}</strong>
              <span>{{ device.id }} / {{ device.workshop }}</span>
            </div>
            <StatusPill :value="device.status" />
            <div class="row-actions">
              <button class="mini-button" type="button" :disabled="Boolean(actionLoading)" @click="store.setDeviceStatus(device, 'in_use')">运行</button>
              <button class="mini-button" type="button" :disabled="Boolean(actionLoading)" @click="store.setDeviceStatus(device, 'maintenance')">维护</button>
              <button class="mini-button" type="button" :disabled="Boolean(actionLoading)" @click="store.setDeviceStatus(device, 'available')">待机</button>
            </div>
          </article>
        </div>
      </div>

      <div class="stack">
        <div class="panel">
          <div class="panel-header">
            <h2>预约审批</h2>
            <span class="count">{{ data.reservations.length }} 单</span>
          </div>
          <div class="panel-body compact-list">
            <article v-for="item in data.reservations" :key="item.id">
              <div>
                <strong>{{ item.device }}</strong>
                <span>{{ item.slot }} / {{ item.applicant }}</span>
              </div>
              <StatusPill :value="item.status" />
              <div class="row-actions">
                <button class="mini-button primary" type="button" :disabled="item.status !== '待审核' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'approve')"><Check :size="14" />通过</button>
                <button class="mini-button" type="button" :disabled="item.status !== '待审核' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'reject')"><X :size="14" />驳回</button>
              </div>
            </article>
            <DataState v-if="data.reservations.length === 0" empty empty-text="暂无预约记录" />
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h2>维修工单</h2>
            <span class="count">{{ activeOrders.length }} 张</span>
          </div>
          <div class="panel-body compact-list">
            <article v-for="order in activeOrders" :key="order.id">
              <div>
                <strong>{{ order.title }}</strong>
                <span>{{ order.device }} / {{ order.id }}</span>
              </div>
              <StatusPill :value="order.status" />
              <div class="row-actions">
                <button class="mini-button" type="button" :disabled="order.status !== '待派工' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(order, 'processing')">开始</button>
                <button class="mini-button primary" type="button" :disabled="order.status !== '处理中' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(order, 'finished')">完成</button>
                <button class="mini-button" type="button" :disabled="order.status === '已关闭' || Boolean(actionLoading)" @click="store.changeWorkOrderStatus(order, 'closed')">关闭</button>
              </div>
            </article>
            <DataState v-if="activeOrders.length === 0" empty empty-text="暂无打开工单" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.owner-metric {
  display: grid;
  min-height: 104px;
  grid-template-columns: auto 1fr;
  gap: 6px 12px;
  align-items: center;
  padding: 18px;
}

.owner-metric svg {
  grid-row: span 2;
  color: var(--blue);
}

.owner-metric strong {
  color: #172033;
  font-size: 30px;
}

.owner-metric span,
.count,
.chart-note {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.chart-note {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.device-list,
.compact-list,
.stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.device-row,
.compact-list article {
  display: grid;
  align-items: center;
  gap: 12px;
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.device-row {
  grid-template-columns: minmax(0, 1fr) 86px auto;
}

.compact-list article {
  grid-template-columns: minmax(0, 1fr) auto auto;
}

.device-row strong,
.compact-list strong {
  display: block;
  overflow: hidden;
  color: #1d2a3e;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.device-row span,
.compact-list span {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 13px;
}

@media (max-width: 720px) {
  .device-row,
  .compact-list article {
    grid-template-columns: 1fr;
  }
}
</style>
