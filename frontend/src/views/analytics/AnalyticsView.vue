<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';

import ChartPanel from '@/components/common/ChartPanel.vue';
import DataState from '@/components/common/DataState.vue';
import { useOperationsStore } from '@/stores/operations';

const { data, loading, error, source } = storeToRefs(useOperationsStore());

const oeeOption = computed<EChartsOption>(() => ({
  color: ['#1769e0', '#19a974', '#f59e0b'],
  tooltip: { trigger: 'axis' },
  legend: { top: 0, right: 10 },
  grid: { left: 42, right: 18, top: 46, bottom: 34 },
  xAxis: { type: 'category', data: data.value.productionRecords.map((item) => item.line) },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#edf2f7' } } },
  series: [
    { name: '合格率', type: 'bar', data: data.value.productionRecords.map((item) => item.passRate), barWidth: 18 },
    { name: 'OEE', type: 'bar', data: data.value.productionRecords.map((item) => item.oee), barWidth: 18 }
  ]
}));

const energyOption = computed<EChartsOption>(() => ({
  color: ['#00a6c8', '#7654d8', '#f59e0b', '#19a974'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 4 },
  series: [
    {
      name: '能耗',
      type: 'pie',
      radius: ['45%', '68%'],
      center: ['50%', '45%'],
      data: data.value.productionRecords.map((item) => ({ name: item.line, value: item.energy })),
      label: { formatter: '{b}\n{d}%' }
    }
  ]
}));
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">数据决策</p>
        <h1>产线效率与能耗分析</h1>
        <p class="subtle">沉淀产量、合格率、OEE 与能耗指标，便于后续接入 BI 或设备采集服务。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <select class="field" aria-label="时间范围">
          <option>近 7 天</option>
          <option>近 30 天</option>
          <option>本季度</option>
        </select>
      </div>
    </section>

    <DataState :loading="loading" :error="error" :empty="data.productionRecords.length === 0" empty-text="暂无分析数据" />

    <section class="grid two">
      <ChartPanel title="产线质量与 OEE" :option="oeeOption" />
      <ChartPanel title="能耗占比" :option="energyOption" />
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>产线指标明细</h2>
      </div>
      <div class="panel-body table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>产线</th>
              <th>产量</th>
              <th>合格率</th>
              <th>OEE</th>
              <th>能耗 kWh</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data.productionRecords" :key="item.line">
              <td class="strong">{{ item.line }}</td>
              <td>{{ item.output }}</td>
              <td>{{ item.passRate }}%</td>
              <td>{{ item.oee }}%</td>
              <td>{{ item.energy }}</td>
            </tr>
            <tr v-if="data.productionRecords.length === 0">
              <td colspan="5">暂无分析数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
