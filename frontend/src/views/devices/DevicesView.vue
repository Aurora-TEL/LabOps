<script setup lang="ts">
import { Cpu, Filter, Plus } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';

import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const { data } = storeToRefs(useOperationsStore());
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">设备台账</p>
        <h1>设备状态与维护计划</h1>
        <p class="subtle">展示设备运行、利用率、温度和下次保养时间，后续可接入实时采集数据。</p>
      </div>
      <div class="toolbar">
        <button class="text-button" type="button"><Filter :size="17" />筛选</button>
        <button class="text-button primary" type="button"><Plus :size="17" />新增设备</button>
      </div>
    </section>

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
