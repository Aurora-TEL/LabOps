<script setup lang="ts">
import { CalendarPlus, Check, RefreshCw, X } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, reactive, ref } from 'vue';

import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);
const showForm = ref(false);
const statusFilter = ref('全部状态');
const start = new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16);
const end = new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString().slice(0, 16);
const form = reactive({
  device_id: '',
  start_time: start,
  end_time: end,
  purpose: '样品检测与参数验证'
});

const filteredReservations = computed(() =>
  statusFilter.value === '全部状态' ? data.value.reservations : data.value.reservations.filter((item) => item.status === statusFilter.value)
);

function selectedDeviceId() {
  return form.device_id || data.value.deviceStatuses[0]?.rawId || data.value.deviceStatuses[0]?.id || '';
}

async function submitReservation() {
  await store.createReservation({
    device_id: selectedDeviceId(),
    start_time: new Date(form.start_time).toISOString(),
    end_time: new Date(form.end_time).toISOString(),
    purpose: form.purpose
  });
  showForm.value = false;
}
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">预约排程</p>
        <h1>设备预约列表</h1>
        <p class="subtle">用于展示申请人、部门、预约时段与审核状态，可演示创建、审批、拒绝和取消。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' ? '后端接口' : '演示数据' }}</span>
        <select v-model="statusFilter" class="field" aria-label="状态">
          <option>全部状态</option>
          <option>待审核</option>
          <option>已确认</option>
          <option>进行中</option>
          <option>已完成</option>
        </select>
        <button class="text-button" type="button" :disabled="loading" @click="store.refresh"><RefreshCw :size="17" />刷新</button>
        <button class="text-button primary" type="button" @click="showForm = !showForm"><CalendarPlus :size="17" />新建预约</button>
      </div>
    </section>

    <section v-if="showForm" class="panel">
      <form class="inline-form compact" @submit.prevent="submitReservation">
        <label class="form-item">
          预约设备
          <select v-model="form.device_id" required>
            <option disabled value="">请选择设备</option>
            <option v-for="device in data.deviceStatuses" :key="device.id" :value="device.rawId ?? device.id">{{ device.name }}</option>
          </select>
        </label>
        <label class="form-item">开始时间<input v-model="form.start_time" required type="datetime-local" /></label>
        <label class="form-item">结束时间<input v-model="form.end_time" required type="datetime-local" /></label>
        <label class="form-item">用途<input v-model.trim="form.purpose" required /></label>
        <button class="text-button primary" type="submit" :disabled="actionLoading === 'reservation:create'">
          {{ actionLoading === 'reservation:create' ? '提交中' : '提交' }}
        </button>
      </form>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading" :error="error" :empty="filteredReservations.length === 0" empty-text="暂无预约记录" />

    <section class="panel">
      <div class="panel-header">
        <h2>预约明细</h2>
        <span class="count">{{ filteredReservations.length }} 条记录</span>
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
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredReservations" :key="item.id">
              <td class="strong">{{ item.id }}</td>
              <td>{{ item.device }}</td>
              <td>{{ item.applicant }}</td>
              <td>{{ item.department }}</td>
              <td>{{ item.slot }}</td>
              <td><StatusPill :value="item.status" /></td>
              <td>
                <div class="row-actions">
                  <button class="mini-button primary" type="button" :disabled="item.status !== '待审核' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'approve')"><Check :size="14" />通过</button>
                  <button class="mini-button" type="button" :disabled="item.status !== '待审核' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'reject')"><X :size="14" />拒绝</button>
                  <button class="mini-button" type="button" :disabled="item.status === '已完成' || Boolean(actionLoading)" @click="store.changeReservationStatus(item, 'cancel')">取消</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredReservations.length === 0">
              <td colspan="7">暂无预约记录</td>
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
