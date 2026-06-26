<script setup lang="ts">
import * as echarts from 'echarts/core';
import { BarChart, GaugeChart, LineChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TooltipComponent
} from 'echarts/components';
import type { EChartsOption } from 'echarts';
import type { ECharts } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';

echarts.use([BarChart, GaugeChart, GridComponent, LegendComponent, LineChart, PieChart, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
  title: string;
  option: EChartsOption;
}>();

const el = ref<HTMLDivElement>();
const chart = shallowRef<ECharts>();

function resizeChart() {
  chart.value?.resize();
}

onMounted(() => {
  if (!el.value) return;
  chart.value = echarts.init(el.value);
  chart.value.setOption(props.option);
  window.addEventListener('resize', resizeChart);
});

watch(
  () => props.option,
  (option) => chart.value?.setOption(option, true),
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chart.value?.dispose();
});
</script>

<template>
  <section class="panel chart-panel">
    <div class="panel-header">
      <h2>{{ title }}</h2>
      <slot name="extra" />
    </div>
    <div ref="el" class="chart"></div>
  </section>
</template>

<style scoped>
.chart-panel {
  min-height: 330px;
}

.chart {
  width: 100%;
  height: 276px;
}
</style>
