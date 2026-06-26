<script setup lang="ts">
import { ClipboardPlus, SlidersHorizontal } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';

import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const { data, loading, error, source } = storeToRefs(useOperationsStore());

const columns = ['待派工', '处理中', '待验收', '已关闭'];
const groupedOrders = computed(() =>
  columns.map((status) => ({
    status,
    items: data.value.repairOrders.filter((item) => item.status === status)
  }))
);
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">运维闭环</p>
        <h1>报修工单看板</h1>
        <p class="subtle">按照派工、处理、验收到关闭的流程呈现，方便答辩演示运维闭环。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <button class="text-button" type="button"><SlidersHorizontal :size="17" />流程配置</button>
        <button class="text-button primary" type="button"><ClipboardPlus :size="17" />提交报修</button>
      </div>
    </section>

    <DataState :loading="loading" :error="error" :empty="data.repairOrders.length === 0" empty-text="暂无报修工单" />

    <section class="kanban">
      <div v-for="column in groupedOrders" :key="column.status" class="panel lane">
        <div class="lane-header">
          <h2>{{ column.status }}</h2>
          <span>{{ column.items.length }}</span>
        </div>
        <article v-for="item in column.items" :key="item.id" class="ticket">
          <div class="ticket-top">
            <StatusPill :value="item.priority" />
            <span>{{ item.createdAt }}</span>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.device }}</p>
          <footer>
            <strong>{{ item.assignee }}</strong>
            <span>{{ item.id }}</span>
          </footer>
        </article>
        <div v-if="column.items.length === 0" class="empty">暂无工单</div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.kanban {
  display: grid;
  grid-template-columns: repeat(4, minmax(220px, 1fr));
  gap: 16px;
  overflow-x: auto;
}

.lane {
  min-height: 430px;
  padding: 14px;
}

.lane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.lane-header span {
  display: inline-flex;
  min-width: 28px;
  height: 28px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  color: var(--blue);
  background: #e8f1ff;
  font-weight: 900;
}

.ticket {
  border: 1px solid #e4edf7;
  border-radius: 8px;
  background: #fbfdff;
  padding: 14px;
}

.ticket + .ticket,
.empty {
  margin-top: 12px;
}

.ticket-top,
.ticket footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.ticket-top span,
.ticket p,
.ticket footer span {
  color: var(--muted);
  font-size: 13px;
}

.ticket h3 {
  margin-top: 14px;
  line-height: 1.5;
}

.ticket p {
  margin-bottom: 16px;
}

.ticket footer strong {
  color: #172033;
}

.empty {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: center;
  border: 1px dashed #cfdceb;
  border-radius: 8px;
  color: var(--muted);
  background: #f8fbff;
  font-weight: 800;
}
</style>
