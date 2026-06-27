<script setup lang="ts">
import { CalendarPlus, ClipboardPlus, RefreshCw, X } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, reactive, ref } from 'vue';

import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useAuthStore } from '@/stores/auth';
import { useOperationsStore } from '@/stores/operations';

const authStore = useAuthStore();
const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);

const showReservationForm = ref(false);
const showRepairForm = ref(false);
const start = new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16);
const end = new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString().slice(0, 16);

const reservationForm = reactive({
  device_id: '',
  start_time: start,
  end_time: end,
  purpose: '实验样品测试与参数验证'
});

const repairForm = reactive({
  device_id: '',
  fault_type: 'hardware',
  description: '设备运行异常，请安排检查'
});

const availableDevices = computed(() => data.value.deviceStatuses.filter((device) => device.status !== '离线'));
const activeReservations = computed(() => data.value.reservations.filter((item) => item.status !== '已完成'));
const recentRepairs = computed(() => data.value.repairReports.slice(0, 6));

function selectedDeviceId(deviceId: string) {
  return deviceId || availableDevices.value[0]?.rawId || availableDevices.value[0]?.id || '';
}

async function submitReservation() {
  await store.createReservation({
    device_id: selectedDeviceId(reservationForm.device_id),
    start_time: new Date(reservationForm.start_time).toISOString(),
    end_time: new Date(reservationForm.end_time).toISOString(),
    purpose: reservationForm.purpose
  });
  showReservationForm.value = false;
}

async function submitRepair() {
  await store.createRepairReport({
    device_id: selectedDeviceId(repairForm.device_id),
    fault_type: repairForm.fault_type,
    description: repairForm.description
  });
  showRepairForm.value = false;
}
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">普通用户自助台</p>
        <h1>{{ authStore.displayName }} 的实验预约与报修</h1>
        <p class="subtle">面向学生和普通实验用户，聚焦设备查询、预约申请、报修提交和状态跟踪。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <button class="text-button" type="button" :disabled="loading" @click="store.refresh"><RefreshCw :size="17" />刷新</button>
        <button class="text-button" type="button" @click="showRepairForm = !showRepairForm"><ClipboardPlus :size="17" />提交报修</button>
        <button class="text-button primary" type="button" @click="showReservationForm = !showReservationForm"><CalendarPlus :size="17" />新建预约</button>
      </div>
    </section>

    <section class="grid metrics">
      <div class="panel user-metric">
        <strong>{{ availableDevices.length }}</strong>
        <span>可预约设备</span>
      </div>
      <div class="panel user-metric">
        <strong>{{ activeReservations.length }}</strong>
        <span>进行中的预约</span>
      </div>
      <div class="panel user-metric">
        <strong>{{ recentRepairs.length }}</strong>
        <span>我的报修记录</span>
      </div>
      <div class="panel user-metric">
        <strong>{{ data.repairReports.filter((item) => item.status !== '已关闭').length }}</strong>
        <span>待处理报修</span>
      </div>
    </section>

    <section v-if="showReservationForm" class="panel">
      <form class="inline-form compact" @submit.prevent="submitReservation">
        <label class="form-item">
          预约设备
          <select v-model="reservationForm.device_id" required>
            <option disabled value="">请选择设备</option>
            <option v-for="device in availableDevices" :key="device.id" :value="device.rawId ?? device.id">{{ device.name }}</option>
          </select>
        </label>
        <label class="form-item">开始时间<input v-model="reservationForm.start_time" required type="datetime-local" /></label>
        <label class="form-item">结束时间<input v-model="reservationForm.end_time" required type="datetime-local" /></label>
        <label class="form-item">用途<input v-model.trim="reservationForm.purpose" required /></label>
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'reservation:create'">
          {{ actionLoading === 'reservation:create' ? '提交中' : '提交预约' }}
        </button>
      </form>
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
          {{ actionLoading === 'repair:create' ? '提交中' : '提交报修' }}
        </button>
      </form>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading" :error="error" :empty="data.deviceStatuses.length === 0" empty-text="暂无可用设备" />

    <section class="grid two">
      <div class="panel">
        <div class="panel-header">
          <h2>可预约设备</h2>
          <span class="count">{{ availableDevices.length }} 台</span>
        </div>
        <div class="panel-body device-list">
          <article v-for="device in availableDevices" :key="device.id" class="device-row">
            <div>
              <strong>{{ device.name }}</strong>
              <span>{{ device.id }} / {{ device.workshop }}</span>
            </div>
            <StatusPill :value="device.status" />
            <div class="device-util">
              <span>{{ device.utilization }}%</span>
              <div class="progress"><span :style="{ width: `${device.utilization}%` }"></span></div>
            </div>
          </article>
        </div>
      </div>

      <div class="stack">
        <div class="panel">
          <div class="panel-header">
            <h2>我的预约</h2>
            <span class="count">{{ data.reservations.length }} 单</span>
          </div>
          <div class="panel-body compact-list">
            <article v-for="item in data.reservations" :key="item.id">
              <div>
                <strong>{{ item.device }}</strong>
                <span>{{ item.slot }} / {{ item.id }}</span>
              </div>
              <StatusPill :value="item.status" />
              <button class="mini-button" type="button" :disabled="item.status === '已完成' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'cancel')">
                <X :size="14" />取消
              </button>
            </article>
            <DataState v-if="data.reservations.length === 0" empty empty-text="暂无预约记录" />
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h2>我的报修</h2>
            <span class="count">{{ recentRepairs.length }} 条</span>
          </div>
          <div class="panel-body compact-list">
            <article v-for="report in recentRepairs" :key="report.id">
              <div>
                <strong>{{ report.device }}</strong>
                <span>{{ report.description }}</span>
              </div>
              <StatusPill :value="report.status" />
            </article>
            <DataState v-if="recentRepairs.length === 0" empty empty-text="暂无报修记录" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.user-metric {
  display: flex;
  min-height: 96px;
  flex-direction: column;
  justify-content: center;
  padding: 18px;
}

.user-metric strong {
  color: var(--blue);
  font-size: 30px;
}

.user-metric span,
.count {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
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
  grid-template-columns: minmax(0, 1.1fr) 90px minmax(120px, 0.7fr);
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

.device-util > span {
  margin-bottom: 8px;
  color: #243249;
  font-weight: 900;
}

@media (max-width: 720px) {
  .device-row,
  .compact-list article {
    grid-template-columns: 1fr;
  }
}
</style>
