<script setup lang="ts">
import { Cpu, FileClock, Plus, RefreshCw } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, reactive, ref } from 'vue';

import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';
import { createMaintenanceRecord, getMaintenanceRecords, type BackendDeviceStatus, type BackendMaintenanceType } from '@/api/operations';
import type { DeviceStatus, MaintenanceRecord } from '@/types';

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);
const showForm = ref(false);
const selectedDevice = ref<DeviceStatus | null>(null);
const maintenanceRecords = ref<MaintenanceRecord[]>([]);
const maintenanceLoading = ref(false);
const maintenanceError = ref('');
const form = reactive({
  code: `DEV-${Math.floor(Math.random() * 900 + 100)}`,
  name: '演示设备',
  status: 'available' as BackendDeviceStatus,
  health_score: 88,
  purchase_date: new Date().toISOString().slice(0, 10)
});
const maintenanceForm = reactive({
  maintenance_type: 'routine' as BackendMaintenanceType,
  title: '例行保养检查',
  content: '检查设备外观、关键部件、运行噪声和安全防护状态。',
  result: '状态正常',
  next_maintenance_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16)
});

const selectedRawDeviceId = computed(() => selectedDevice.value?.rawId ?? selectedDevice.value?.id ?? '');

const maintenanceTypeLabels: Record<BackendMaintenanceType, string> = {
  routine: '例行保养',
  repair: '维修',
  calibration: '校准',
  replacement: '更换',
  enable: '启用',
  disable: '停用'
};

function formatDateTime(value?: string | null) {
  if (!value) return '未计划';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

async function submitDevice() {
  await store.createDevice({
    code: form.code,
    name: form.name,
    status: form.status,
    health_score: form.health_score,
    purchase_date: form.purchase_date || null
  });
  showForm.value = false;
}

async function openDeviceDetail(device: DeviceStatus) {
  selectedDevice.value = device;
  maintenanceLoading.value = true;
  maintenanceError.value = '';
  try {
    maintenanceRecords.value = await getMaintenanceRecords(device.rawId ?? device.id);
  } catch (error) {
    maintenanceRecords.value = [];
    maintenanceError.value = error instanceof Error ? `${error.message}，暂无维护记录` : '维护记录暂不可用';
  } finally {
    maintenanceLoading.value = false;
  }
}

async function submitMaintenanceRecord() {
  if (!selectedDevice.value) return;
  store.beginAction('maintenance:create');
  maintenanceError.value = '';
  try {
    const created = await createMaintenanceRecord({
      device_id: selectedRawDeviceId.value,
      maintenance_type: maintenanceForm.maintenance_type,
      title: maintenanceForm.title,
      content: maintenanceForm.content,
      result: maintenanceForm.result,
      next_maintenance_at: maintenanceForm.next_maintenance_at ? new Date(maintenanceForm.next_maintenance_at).toISOString() : null
    });
    maintenanceRecords.value.unshift({
      id: `MTN-${created.id.slice(0, 8)}`,
      rawId: created.id,
      rawDeviceId: created.device_id,
      type: created.maintenance_type,
      title: created.title,
      content: created.content,
      result: created.result,
      costAmount: created.cost_amount,
      maintainedAt: created.maintained_at,
      nextMaintenanceAt: created.next_maintenance_at
    });
    store.success = '维护记录已创建';
  } catch (error) {
    maintenanceError.value = error instanceof Error ? error.message : '维护记录创建失败';
  } finally {
    store.endAction();
  }
}
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">设备台账</p>
        <h1>设备状态与维护计划</h1>
        <p class="subtle">展示设备运行、利用率、温度和下次保养时间，支持演示级创建和状态切换。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <button class="text-button" type="button" :disabled="loading" @click="store.refresh"><RefreshCw :size="17" />刷新</button>
        <button class="text-button primary" type="button" @click="showForm = !showForm"><Plus :size="17" />新增设备</button>
      </div>
    </section>

    <section v-if="showForm" class="panel">
      <form class="inline-form" @submit.prevent="submitDevice">
        <label class="form-item">设备编号<input v-model.trim="form.code" required /></label>
        <label class="form-item">设备名称<input v-model.trim="form.name" required /></label>
        <label class="form-item">
          初始状态
          <select v-model="form.status">
            <option value="available">可预约</option>
            <option value="in_use">使用中</option>
            <option value="maintenance">维护中</option>
            <option value="disabled">停用</option>
          </select>
        </label>
        <label class="form-item">健康分<input v-model.number="form.health_score" min="0" max="100" type="number" /></label>
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'device:create'">
          {{ actionLoading === 'device:create' ? '提交中' : '保存' }}
        </button>
      </form>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading" :error="error" :empty="data.deviceStatuses.length === 0" empty-text="暂无设备台账" />

    <section class="device-grid">
      <article v-for="device in data.deviceStatuses" :key="device.id" class="panel device-card">
        <div class="device-title">
          <span><Cpu :size="20" /></span>
          <StatusPill :value="device.status" />
        </div>
        <h2>{{ device.name }}</h2>
        <p>{{ device.id }} · {{ device.workshop }}</p>
        <div class="telemetry">
          <div><strong>{{ device.utilization }}%</strong><span>利用率</span></div>
          <div><strong>{{ device.temperature }}℃</strong><span>温度</span></div>
          <div><strong>{{ device.nextMaintenance }}</strong><span>下次保养</span></div>
        </div>
        <div class="progress"><span :style="{ width: `${device.utilization}%` }"></span></div>
        <div class="row-actions">
          <button class="mini-button" type="button" :disabled="actionLoading === `device:${device.id}`" @click="store.setDeviceStatus(device, 'in_use')">运行</button>
          <button class="mini-button" type="button" :disabled="actionLoading === `device:${device.id}`" @click="store.setDeviceStatus(device, 'maintenance')">维护</button>
          <button class="mini-button" type="button" :disabled="actionLoading === `device:${device.id}`" @click="store.setDeviceStatus(device, 'available')">待机</button>
          <button class="mini-button primary" type="button" @click="openDeviceDetail(device)">详情</button>
        </div>
      </article>
    </section>

    <section v-if="selectedDevice" class="panel detail-panel">
      <div class="panel-header">
        <div>
          <h2>{{ selectedDevice.name }} 维护台账</h2>
          <p class="subtle">{{ selectedDevice.id }} · {{ selectedDevice.workshop }} · 健康分 {{ selectedDevice.utilization }}</p>
        </div>
        <StatusPill :value="selectedDevice.status" />
      </div>
      <div class="detail-layout">
        <div class="detail-summary">
          <div><strong>{{ selectedDevice.temperature }}℃</strong><span>实时温度</span></div>
          <div><strong>{{ selectedDevice.nextMaintenance }}</strong><span>计划保养</span></div>
          <div><strong>{{ maintenanceRecords.length }}</strong><span>维护记录</span></div>
        </div>

        <form class="maintenance-form" @submit.prevent="submitMaintenanceRecord">
          <label class="form-item">
            类型
            <select v-model="maintenanceForm.maintenance_type">
              <option value="routine">例行保养</option>
              <option value="repair">维修</option>
              <option value="calibration">校准</option>
              <option value="replacement">更换</option>
            </select>
          </label>
          <label class="form-item">标题<input v-model.trim="maintenanceForm.title" required /></label>
          <label class="form-item">下次保养<input v-model="maintenanceForm.next_maintenance_at" type="datetime-local" /></label>
          <label class="form-item wide">内容<textarea v-model.trim="maintenanceForm.content" required rows="2" /></label>
          <label class="form-item wide">结果<textarea v-model.trim="maintenanceForm.result" rows="2" /></label>
          <button class="text-button primary" type="submit" :disabled="actionLoading === 'maintenance:create'">
            <FileClock :size="16" />{{ actionLoading === 'maintenance:create' ? '保存中' : '新增记录' }}
          </button>
        </form>
      </div>

      <div v-if="maintenanceError" class="data-state warning">{{ maintenanceError }}</div>
      <DataState :loading="maintenanceLoading" :empty="!maintenanceLoading && maintenanceRecords.length === 0" empty-text="暂无维护记录" />
      <div class="maintenance-list">
        <article v-for="record in maintenanceRecords" :key="record.id" class="maintenance-item">
          <div>
            <strong>{{ record.title }}</strong>
            <span>{{ maintenanceTypeLabels[record.type] }} / {{ formatDateTime(record.maintainedAt) }}</span>
          </div>
          <p>{{ record.content }}</p>
          <small>{{ record.result || '未填写结果' }} · 下次 {{ formatDateTime(record.nextMaintenanceAt) }}</small>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.device-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.device-card {
  padding: 18px;
}

.device-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.device-title > span {
  display: inline-flex;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
}

.device-card h2 {
  margin-bottom: 8px;
}

.device-card p {
  min-height: 42px;
  color: var(--muted);
  line-height: 1.5;
}

.telemetry {
  display: grid;
  gap: 10px;
  margin: 18px 0;
}

.telemetry div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 8px;
  background: #f5f9fe;
  padding: 10px;
}

.telemetry strong {
  color: #172033;
}

.telemetry span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.row-actions {
  margin-top: 14px;
}

.detail-panel {
  overflow: hidden;
}

.detail-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 16px;
  padding: 18px;
}

.detail-summary {
  display: grid;
  gap: 10px;
}

.detail-summary div,
.maintenance-item {
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.detail-summary strong {
  display: block;
  color: var(--blue);
  font-size: 22px;
}

.detail-summary span,
.maintenance-item span,
.maintenance-item small {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.maintenance-form {
  display: grid;
  grid-template-columns: repeat(3, minmax(160px, 1fr)) auto;
  gap: 12px;
  align-items: end;
}

.maintenance-form .wide {
  grid-column: span 2;
}

.maintenance-list {
  display: grid;
  gap: 10px;
  padding: 0 18px 18px;
}

.maintenance-item {
  display: grid;
  grid-template-columns: minmax(180px, 0.7fr) minmax(0, 1fr) minmax(180px, 0.6fr);
  gap: 12px;
  align-items: center;
}

.maintenance-item strong {
  display: block;
  color: #172033;
}

.maintenance-item p {
  margin: 0;
  color: #40516a;
  line-height: 1.55;
}

@media (max-width: 1180px) {
  .device-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .device-grid {
    grid-template-columns: 1fr;
  }

  .detail-layout,
  .maintenance-form,
  .maintenance-item {
    grid-template-columns: 1fr;
  }

  .maintenance-form .wide {
    grid-column: auto;
  }
}
</style>
