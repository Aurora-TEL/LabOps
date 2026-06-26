<script setup lang="ts">
import { CalendarPlus, Download, Filter } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';

import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const { data } = storeToRefs(useOperationsStore());
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">预约排程</p>
        <h1>设备预约列表</h1>
        <p class="subtle">用于展示申请人、部门、预约时段与审核状态，后续可接入审批和冲突校验接口。</p>
      </div>
      <div class="toolbar">
        <select class="field" aria-label="状态">
          <option>全部状态</option>
          <option>待审核</option>
          <option>已确认</option>
          <option>进行中</option>
        </select>
        <button class="icon-button" type="button" title="筛选"><Filter :size="18" /></button>
        <button class="text-button" type="button"><Download :size="17" />导出</button>
        <button class="text-button primary" type="button"><CalendarPlus :size="17" />新建预约</button>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>今日预约明细</h2>
        <span class="count">{{ data.reservations.length }} 条记录</span>
      </div>
      <div class="panel-body table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>预约单号</th>
              <th>设备</th>
              <th>申请人</th>
              <th>部门</th>
              <th>时段</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data.reservations" :key="item.id">
              <td class="strong">{{ item.id }}</td>
              <td>{{ item.device }}</td>
              <td>{{ item.applicant }}</td>
              <td>{{ item.department }}</td>
              <td>{{ item.slot }}</td>
              <td><StatusPill :value="item.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.count {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}
</style>
