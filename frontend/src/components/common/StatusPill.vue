<script setup lang="ts">
defineProps<{
  value: string;
}>();
</script>

<template>
  <span class="status-pill" :class="value">
    {{ value }}
  </span>
</template>

<style scoped>
.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  min-height: 26px;
  border-radius: 999px;
  padding: 0 10px;
  color: #376071;
  background: #e8f5f8;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.运行中,
.已确认,
.已完成,
.已关闭 {
  color: #0d7b55;
  background: #def8ec;
}

.待机,
.待审核,
.待派工 {
  color: #9a6400;
  background: #fff3cf;
}

.维护中,
.进行中,
.处理中,
.待验收 {
  color: #1769e0;
  background: #e5f0ff;
}

.离线,
.高 {
  color: #bd2d35;
  background: #ffe4e5;
}

.中 {
  color: #8c5b00;
  background: #fff1cf;
}

.低 {
  color: #477389;
  background: #e7f5fb;
}
</style>
