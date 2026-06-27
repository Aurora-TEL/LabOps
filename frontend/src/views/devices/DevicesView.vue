<script setup lang="ts">
import { Cpu, Plus, RefreshCw } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { reactive, ref } from 'vue';

import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';
import type { BackendDeviceStatus } from '@/api/operations';

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);
const showForm = ref(false);
const form = reactive({
  code: `DEV-${Math.floor(Math.random() * 900 + 100)}`,
  name: '演示设备',
  status: 'available' as BackendDeviceStatus,
  health_score: 88,
  purchase_date: new Date().toISOString().slice(0, 10)
});

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
        </div>
      </article>
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

@media (max-width: 1180px) {
  .device-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .device-grid {
    grid-template-columns: 1fr;
  }
}
</style>
