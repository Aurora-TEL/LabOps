<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { storeToRefs } from 'pinia';
import { Activity, CalendarCheck, ClipboardList, RefreshCw } from 'lucide-vue-next';
import { computed, onMounted } from 'vue';

import ChartPanel from '@/components/common/ChartPanel.vue';
import MetricCard from '@/components/common/MetricCard.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const store = useOperationsStore();
const { data } = storeToRefs(store);

onMounted(() => store.load());

const usageOption = computed<EChartsOption>(() => ({
  color: ['#1769e0'],
  tooltip: { trigger: 'axis' },
  grid: { left: 36, right: 18, top: 28, bottom: 32 },
  xAxis: { type: 'category', data: data.value.weeklyUsage.map((item) => item.name), axisTick: { show: false } },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [
    {
      type: 'bar',
      barWidth: 28,
      data: data.value.weeklyUsage.map((item) => item.value),
      itemStyle: { borderRadius: [6, 6, 0, 0] }
    }
  ]
}));

const repairOption = computed<EChartsOption>(() => ({
  color: ['#00a6c8', '#7654d8'],
  tooltip: { trigger: 'axis' },
  grid: { left: 38, right: 18, top: 28, bottom: 32 },
  xAxis: { type: 'category', data: data.value.orderTrend.map((item) => item.name), boundaryGap: false },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [
    {
      name: '报修工单',
      type: 'line',
      smooth: true,
      symbolSize: 8,
      areaStyle: { opacity: 0.12 },
      data: data.value.orderTrend.map((item) => item.value)
    }
  ]
}));
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">实时运营总览</p>
        <h1>设备、预约、工单一屏掌握</h1>
        <p class="subtle">面向实验室与制造现场的轻量 ERP 看板，沉淀后续 API 对接的数据结构。</p>
      </div>
      <div class="toolbar">
        <button class="text-button" type="button"><RefreshCw :size="17" />刷新数据</button>
        <button class="text-button primary" type="button"><ClipboardList :size="17" />新建工单</button>
      </div>
    </section>

    <section class="grid metrics">
      <MetricCard v-for="metric in data.metrics" :key="metric.label" :metric="metric" />
    </section>

    <section class="grid two">
      <ChartPanel title="本周设备利用率" :option="usageOption">
        <template #extra><span class="chart-note"><Activity :size="16" />峰值 86%</span></template>
      </ChartPanel>
      <ChartPanel title="工单趋势" :option="repairOption">
        <template #extra><span class="chart-note"><CalendarCheck :size="16" />月度统计</span></template>
      </ChartPanel>
    </section>

    <section class="grid two">
      <div class="panel">
        <div class="panel-header">
          <h2>设备状态</h2>
          <RouterLink to="/devices" class="mini-link">查看全部</RouterLink>
        </div>
        <div class="panel-body device-list">
          <article v-for="device in data.deviceStatuses" :key="device.id" class="device-row">
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
            <h2>今日预约</h2>
            <RouterLink to="/reservations" class="mini-link">排程</RouterLink>
          </div>
          <div class="panel-body compact-list">
            <article v-for="item in data.reservations" :key="item.id">
              <div>
                <strong>{{ item.device }}</strong>
                <span>{{ item.applicant }} · {{ item.slot }}</span>
              </div>
              <StatusPill :value="item.status" />
            </article>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h2>报修工单</h2>
            <RouterLink to="/repairs" class="mini-link">处理</RouterLink>
          </div>
          <div class="panel-body compact-list">
            <article v-for="item in data.repairOrders" :key="item.id">
              <div>
                <strong>{{ item.title }}</strong>
                <span>{{ item.device }} · {{ item.assignee }}</span>
              </div>
              <StatusPill :value="item.status" />
            </article>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.chart-note,
.mini-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.mini-link {
  color: var(--blue);
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
  grid-template-columns: minmax(0, 1fr) auto;
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
  .device-row {
    grid-template-columns: 1fr;
  }
}
</style>
