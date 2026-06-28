<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { BarChart3, Download, RefreshCw } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, onMounted } from 'vue';

import ChartPanel from '@/components/common/ChartPanel.vue';
import DataState from '@/components/common/DataState.vue';
import { useAnalyticsStore } from '@/stores/analytics';

const store = useAnalyticsStore();
const { report, loading, error, source, startDate, endDate, lastUpdated } = storeToRefs(store);

const statusLabels: Record<string, string> = {
  pending: '待审核',
  approved: '已确认',
  rejected: '已拒绝',
  canceled: '已取消',
  completed: '已完成'
};

const typeLabels: Record<string, string> = {
  hardware: '硬件',
  software: '软件',
  network: '网络',
  calibration: '校准',
  routine: '例行保养',
  repair: '维修',
  replacement: '备件更换',
  enable: '启用',
  disable: '停用'
};

const trendOption = computed<EChartsOption>(() => ({
  color: ['#1769e0', '#e5484d'],
  tooltip: { trigger: 'axis' },
  legend: { top: 0, right: 10 },
  grid: { left: 42, right: 18, top: 46, bottom: 34 },
  xAxis: { type: 'category', data: report.value.reservationTrend.map((item) => formatDate(item.date)) },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [
    { name: '预约量', type: 'line', smooth: true, data: report.value.reservationTrend.map((item) => item.value) },
    { name: '报修量', type: 'line', smooth: true, data: report.value.repairTrend.map((item) => item.value) }
  ]
}));

const reservationStatusOption = computed<EChartsOption>(() => ({
  color: ['#1769e0', '#19a974', '#f59e0b', '#7654d8', '#e5484d'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 4 },
  series: [
    {
      name: '预约状态',
      type: 'pie',
      radius: ['45%', '68%'],
      center: ['50%', '45%'],
      data: report.value.reservationStatus.map((item) => ({ name: statusLabels[item.status] ?? item.status, value: item.count })),
      label: { formatter: '{b}\n{d}%' }
    }
  ]
}));

const faultTypeOption = computed<EChartsOption>(() => ({
  color: ['#e5484d'],
  tooltip: { trigger: 'axis' },
  grid: { left: 72, right: 18, top: 24, bottom: 34 },
  xAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f7' } } },
  yAxis: { type: 'category', data: report.value.faultTypes.map((item) => typeLabels[item.name] ?? item.name) },
  series: [{ name: '报修数', type: 'bar', data: report.value.faultTypes.map((item) => item.count), barWidth: 16 }]
}));

const maintenanceOption = computed<EChartsOption>(() => ({
  color: ['#00a6c8', '#19a974', '#f59e0b', '#7654d8'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 4 },
  series: [
    {
      name: '维护类型',
      type: 'pie',
      radius: '62%',
      center: ['50%', '45%'],
      data: report.value.maintenanceTypes.map((item) => ({ name: typeLabels[item.name] ?? item.name, value: item.count }))
    }
  ]
}));

const healthOption = computed<EChartsOption>(() => ({
  color: ['#1769e0'],
  tooltip: { trigger: 'axis' },
  grid: { left: 120, right: 18, top: 24, bottom: 34 },
  xAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: '#edf2f7' } } },
  yAxis: { type: 'category', data: report.value.deviceHealth.map((item) => item.deviceName) },
  series: [{ name: '健康分', type: 'bar', data: report.value.deviceHealth.map((item) => item.healthScore), barWidth: 16 }]
}));

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

function setQuickRange(days: number) {
  const end = new Date();
  const start = new Date(Date.now() - (days - 1) * 24 * 60 * 60 * 1000);
  void store.applyRange(start.toISOString().slice(0, 10), end.toISOString().slice(0, 10));
}

function exportCsv() {
  const rows = [
    ['指标', '数值', '单位', '说明'],
    ...report.value.kpis.map((item) => [item.label, String(item.value), item.unit, item.delta]),
    [],
    ['设备', '状态', '健康分'],
    ...report.value.deviceHealth.map((item) => [item.deviceName, item.status, String(item.healthScore)])
  ];
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `labops-analytics-${report.value.startDate}-${report.value.endDate}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

onMounted(() => {
  if (!store.loaded) void store.load();
});
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">数据决策</p>
        <h1>运营分析报表</h1>
        <p class="subtle">汇总设备健康、预约占用、报修趋势、维护类型和工单闭环，用于复试展示运营决策能力。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <input v-model="startDate" class="field" type="date" aria-label="开始日期" />
        <input v-model="endDate" class="field" type="date" aria-label="结束日期" />
        <button class="text-button" type="button" @click="setQuickRange(7)">近 7 天</button>
        <button class="text-button" type="button" @click="setQuickRange(30)">近 30 天</button>
        <button class="text-button" type="button" :disabled="loading" @click="store.load"><RefreshCw :size="17" />刷新</button>
        <button class="text-button primary" type="button" @click="exportCsv"><Download :size="17" />导出</button>
      </div>
    </section>

    <DataState :loading="loading" :error="error" :empty="report.kpis.length === 0" empty-text="暂无分析数据" />

    <section class="analytics-summary">
      <article v-for="item in report.kpis" :key="item.label" class="panel kpi-card" :class="item.status">
        <span><BarChart3 :size="18" /></span>
        <div>
          <p>{{ item.label }}</p>
          <strong>{{ item.value }}<small>{{ item.unit }}</small></strong>
          <em>{{ item.delta }}</em>
        </div>
      </article>
    </section>

    <section class="report-meta">
      <span>统计区间：{{ report.startDate }} 至 {{ report.endDate }}</span>
      <span>最后刷新：{{ lastUpdated || '待刷新' }}</span>
    </section>

    <section class="grid two">
      <ChartPanel title="预约与报修趋势" :option="trendOption" />
      <ChartPanel title="预约状态分布" :option="reservationStatusOption" />
    </section>

    <section class="grid two">
      <ChartPanel title="故障类型排行" :option="faultTypeOption" />
      <ChartPanel title="维护类型占比" :option="maintenanceOption" />
    </section>

    <section class="grid two">
      <ChartPanel title="设备健康排行" :option="healthOption" />
      <section class="panel">
        <div class="panel-header">
          <h2>健康明细</h2>
        </div>
        <div class="panel-body table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>设备</th>
                <th>状态</th>
                <th>健康分</th>
                <th>风险</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in report.deviceHealth" :key="item.deviceId">
                <td class="strong">{{ item.deviceName }}</td>
                <td>{{ item.status }}</td>
                <td>{{ item.healthScore }}</td>
                <td>{{ item.healthScore < 70 ? '需关注' : '正常' }}</td>
              </tr>
              <tr v-if="report.deviceHealth.length === 0">
                <td colspan="4">暂无设备健康数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </div>
</template>

<style scoped>
.analytics-summary {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.kpi-card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
}

.kpi-card > span {
  display: inline-flex;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
}

.kpi-card.warning > span {
  background: linear-gradient(135deg, var(--orange), #f7b733);
}

.kpi-card p {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.kpi-card strong {
  display: block;
  color: #172033;
  font-size: 25px;
  line-height: 1.1;
}

.kpi-card small {
  margin-left: 4px;
  color: var(--muted);
  font-size: 13px;
}

.kpi-card em {
  display: block;
  margin-top: 8px;
  color: #40516a;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.report-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.report-meta span {
  border: 1px solid #d9e4f1;
  border-radius: 999px;
  background: #fff;
  padding: 7px 12px;
}

@media (max-width: 1180px) {
  .analytics-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .analytics-summary {
    grid-template-columns: 1fr;
  }
}
</style>
