<script setup lang="ts">
import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-vue-next';

import type { Metric } from '@/types';

defineProps<{
  metric: Metric;
}>();
</script>

<template>
  <section class="metric-card" :class="`accent-${metric.accent}`">
    <div class="metric-top">
      <span>{{ metric.label }}</span>
      <ArrowUpRight v-if="metric.trend === 'up'" :size="18" />
      <ArrowDownRight v-else-if="metric.trend === 'down'" :size="18" />
      <ArrowRight v-else :size="18" />
    </div>
    <div class="metric-value">
      {{ metric.value }}<small>{{ metric.unit }}</small>
    </div>
    <p>{{ metric.delta }} 较昨日</p>
  </section>
</template>

<style scoped>
.metric-card {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  border: 1px solid rgba(196, 210, 230, 0.84);
  border-radius: 8px;
  padding: 18px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(247, 251, 255, 0.9)),
    radial-gradient(circle at 85% 20%, rgba(23, 105, 224, 0.16), transparent 28%);
  box-shadow: var(--shadow);
}

.metric-card::after {
  position: absolute;
  right: -22px;
  bottom: -28px;
  width: 110px;
  height: 110px;
  border: 18px solid currentColor;
  border-radius: 50%;
  opacity: 0.08;
  content: "";
}

.metric-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #607086;
  font-size: 14px;
  font-weight: 700;
}

.metric-value {
  margin-top: 24px;
  color: #14233a;
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
}

.metric-value small {
  margin-left: 6px;
  color: #69788e;
  font-size: 15px;
  font-weight: 800;
}

p {
  margin: 12px 0 0;
  color: #718097;
  font-size: 13px;
}

.accent-blue {
  color: var(--blue);
}

.accent-green {
  color: var(--green);
}

.accent-orange {
  color: var(--orange);
}

.accent-violet {
  color: var(--violet);
}
</style>
