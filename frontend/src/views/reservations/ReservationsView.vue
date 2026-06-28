<script setup lang="ts">
import { AlertCircle, CalendarDays, CalendarPlus, Check, Clock3, RefreshCw, X } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import { checkReservationAvailability, getReservationCalendar } from '@/api/operations';
import DataState from '@/components/common/DataState.vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useOperationsStore } from '@/stores/operations';
import type { Reservation, ReservationAvailability, ReservationCalendarItem } from '@/types';

type ViewMode = 'timeline' | 'calendar' | 'list';

interface CalendarEvent {
  id: string;
  reservationNo: string;
  deviceId: string;
  deviceName: string;
  applicantId?: string;
  startTime: string;
  endTime: string;
  purpose: string;
  status: Reservation['status'];
}

const store = useOperationsStore();
const { data, loading, error, success, source, actionLoading } = storeToRefs(store);
const showForm = ref(false);
const statusFilter = ref('全部状态');
const deviceFilter = ref('全部设备');
const viewMode = ref<ViewMode>('timeline');
const selectedDate = ref(toDateInput(new Date()));
const calendarItems = ref<ReservationCalendarItem[]>([]);
const calendarLoading = ref(false);
const calendarError = ref('');
const availability = ref<ReservationAvailability | null>(null);
const availabilityError = ref('');
const start = toDateTimeInput(new Date(Date.now() + 60 * 60 * 1000));
const end = toDateTimeInput(new Date(Date.now() + 3 * 60 * 60 * 1000));
const form = reactive({
  device_id: '',
  start_time: start,
  end_time: end,
  purpose: '样品检测与参数验证'
});

const weekDays = computed(() => {
  const base = new Date(`${selectedDate.value}T00:00:00`);
  const day = base.getDay() || 7;
  const monday = new Date(base);
  monday.setDate(base.getDate() - day + 1);
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(monday);
    date.setDate(monday.getDate() + index);
    return {
      key: toDateInput(date),
      label: date.toLocaleDateString('zh-CN', { weekday: 'short', month: '2-digit', day: '2-digit' })
    };
  });
});

const selectedDevice = computed(() => {
  const selected = selectedDeviceId();
  return data.value.deviceStatuses.find((device) => (device.rawId ?? device.id) === selected || device.id === selected);
});

const selectedDeviceWarning = computed(() => {
  if (!selectedDevice.value) return '';
  if (selectedDevice.value.status === '维护中' || selectedDevice.value.status === '离线') {
    return `${selectedDevice.value.name} 当前${selectedDevice.value.status}，不建议提交预约`;
  }
  return '';
});

const calendarEvents = computed<CalendarEvent[]>(() => {
  const remoteEvents = calendarItems.value.map((item) => ({
    id: item.id,
    reservationNo: item.reservationNo,
    deviceId: item.deviceId,
    deviceName: deviceName(item.deviceId),
    applicantId: item.applicantId,
    startTime: item.startTime,
    endTime: item.endTime,
    purpose: item.purpose,
    status: statusLabel(item.status)
  }));
  if (remoteEvents.length > 0) return remoteEvents;
  return data.value.reservations
    .filter((item) => item.startAt && item.endAt)
    .map((item) => ({
      id: item.rawId ?? item.id,
      reservationNo: item.id,
      deviceId: item.rawDeviceId ?? item.device,
      deviceName: item.device,
      startTime: item.startAt as string,
      endTime: item.endAt as string,
      purpose: item.purpose ?? '设备预约',
      status: item.status
    }));
});

const filteredReservations = computed(() =>
  data.value.reservations.filter((item) => {
    const statusMatched = statusFilter.value === '全部状态' || item.status === statusFilter.value;
    const deviceMatched = deviceFilter.value === '全部设备' || item.rawDeviceId === deviceFilter.value || item.device === deviceFilter.value;
    return statusMatched && deviceMatched;
  })
);

const filteredEvents = computed(() =>
  calendarEvents.value.filter((item) => {
    const statusMatched = statusFilter.value === '全部状态' || item.status === statusFilter.value;
    const deviceMatched = deviceFilter.value === '全部设备' || item.deviceId === deviceFilter.value || item.deviceName === deviceFilter.value;
    return statusMatched && deviceMatched;
  })
);

const deviceRows = computed(() =>
  data.value.deviceStatuses
    .filter((device) => deviceFilter.value === '全部设备' || (device.rawId ?? device.id) === deviceFilter.value || device.id === deviceFilter.value)
    .map((device) => ({
      device,
      events: filteredEvents.value.filter((item) => item.deviceId === (device.rawId ?? device.id) || item.deviceId === device.id || item.deviceName === device.name)
    }))
);

const selectedDayEvents = computed(() => filteredEvents.value.filter((item) => toDateInput(new Date(item.startTime)) === selectedDate.value));

const localAvailabilityBlocked = computed(() => {
  const startAt = new Date(form.start_time);
  const endAt = new Date(form.end_time);
  if (Number.isNaN(startAt.getTime()) || Number.isNaN(endAt.getTime()) || endAt <= startAt) return true;
  return calendarEvents.value.some((item) => {
    if (item.deviceId !== selectedDeviceId() && item.deviceName !== selectedDevice.value?.name) return false;
    if (item.status !== '已确认') return false;
    return new Date(item.startTime) < endAt && new Date(item.endTime) > startAt;
  });
});

const submitDisabled = computed(() =>
  actionLoading.value === 'reservation:create' ||
  Boolean(selectedDeviceWarning.value) ||
  (availability.value !== null ? !availability.value.available : localAvailabilityBlocked.value)
);

function pad(value: number) {
  return String(value).padStart(2, '0');
}

function toDateInput(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function toDateTimeInput(date: Date) {
  return `${toDateInput(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function selectedDeviceId() {
  return form.device_id || data.value.deviceStatuses[0]?.rawId || data.value.deviceStatuses[0]?.id || '';
}

function deviceName(deviceId: string) {
  return data.value.deviceStatuses.find((device) => device.rawId === deviceId || device.id === deviceId)?.name ?? `设备 ${deviceId.slice(0, 6)}`;
}

function statusLabel(status: ReservationCalendarItem['status']): Reservation['status'] {
  const map: Record<ReservationCalendarItem['status'], Reservation['status']> = {
    pending: '待审核',
    approved: '已确认',
    rejected: '已完成',
    canceled: '已完成',
    completed: '已完成'
  };
  return map[status] ?? '待审核';
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function eventStyle(item: CalendarEvent) {
  const dayStart = new Date(`${selectedDate.value}T08:00:00`);
  const dayEnd = new Date(`${selectedDate.value}T22:00:00`);
  const startAt = new Date(item.startTime);
  const endAt = new Date(item.endTime);
  const total = dayEnd.getTime() - dayStart.getTime();
  const left = Math.max(0, Math.min(total, startAt.getTime() - dayStart.getTime()));
  const width = Math.max(30 * 60 * 1000, Math.min(total - left, endAt.getTime() - Math.max(startAt.getTime(), dayStart.getTime())));
  return {
    left: `${(left / total) * 100}%`,
    width: `${(width / total) * 100}%`
  };
}

function eventsForDay(day: string) {
  return filteredEvents.value.filter((item) => toDateInput(new Date(item.startTime)) === day);
}

async function loadCalendar() {
  const rangeStart = new Date(`${weekDays.value[0].key}T00:00:00`).toISOString();
  const rangeEnd = new Date(`${weekDays.value[6].key}T23:59:59`).toISOString();
  calendarLoading.value = true;
  calendarError.value = '';
  try {
    calendarItems.value = await getReservationCalendar({
      start_time: rangeStart,
      end_time: rangeEnd,
      device_id: deviceFilter.value === '全部设备' ? undefined : deviceFilter.value
    });
  } catch (error) {
    calendarItems.value = [];
    calendarError.value = error instanceof Error ? `${error.message}，已使用本地预约数据展示` : '日历接口暂不可用，已使用本地预约数据展示';
  } finally {
    calendarLoading.value = false;
  }
}

async function checkAvailability() {
  availability.value = null;
  availabilityError.value = '';
  try {
    availability.value = await checkReservationAvailability(
      selectedDeviceId(),
      new Date(form.start_time).toISOString(),
      new Date(form.end_time).toISOString()
    );
  } catch (error) {
    availabilityError.value = error instanceof Error ? `${error.message}，已使用本地预约判断` : '可用性接口暂不可用';
  }
}

async function submitReservation() {
  await store.createReservation({
    device_id: selectedDeviceId(),
    start_time: new Date(form.start_time).toISOString(),
    end_time: new Date(form.end_time).toISOString(),
    purpose: form.purpose
  });
  showForm.value = false;
  availability.value = null;
  await loadCalendar();
}

async function refreshAll() {
  await store.refresh();
  await loadCalendar();
}

watch([selectedDate, deviceFilter], () => {
  void loadCalendar();
});

watch(
  () => [form.device_id, form.start_time, form.end_time],
  () => {
    availability.value = null;
    availabilityError.value = '';
  }
);

onMounted(async () => {
  if (!store.loaded) await store.load();
  await loadCalendar();
});
</script>

<template>
  <div class="page">
    <section class="page-header">
      <div>
        <p class="eyebrow">预约排程</p>
        <h1>设备预约日历</h1>
        <p class="subtle">按日历和设备时间轴查看占用，提交预约前可检查指定时段是否冲突。</p>
      </div>
      <div class="toolbar">
        <span class="source-badge">{{ source === 'api' && !calendarError ? '后端接口' : '演示数据' }}</span>
        <input v-model="selectedDate" class="field" type="date" aria-label="日期" />
        <select v-model="deviceFilter" class="field" aria-label="设备">
          <option value="全部设备">全部设备</option>
          <option v-for="device in data.deviceStatuses" :key="device.id" :value="device.rawId ?? device.id">{{ device.name }}</option>
        </select>
        <select v-model="statusFilter" class="field" aria-label="状态">
          <option>全部状态</option>
          <option>待审核</option>
          <option>已确认</option>
          <option>进行中</option>
          <option>已完成</option>
        </select>
        <div class="segmented" aria-label="视图">
          <button type="button" :class="{ active: viewMode === 'timeline' }" @click="viewMode = 'timeline'">时间轴</button>
          <button type="button" :class="{ active: viewMode === 'calendar' }" @click="viewMode = 'calendar'">周历</button>
          <button type="button" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">列表</button>
        </div>
        <button class="text-button" type="button" :disabled="loading || calendarLoading" @click="refreshAll"><RefreshCw :size="17" />刷新</button>
        <button class="text-button primary" type="button" @click="showForm = !showForm"><CalendarPlus :size="17" />新建预约</button>
      </div>
    </section>

    <section v-if="showForm" class="panel">
      <form class="inline-form reservation-form" @submit.prevent="submitReservation">
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
        <div class="form-actions">
          <button class="text-button" type="button" @click="checkAvailability"><Clock3 :size="16" />检查</button>
          <button class="text-button primary" type="submit" :disabled="submitDisabled">
            {{ actionLoading === 'reservation:create' ? '提交中' : '提交' }}
          </button>
        </div>
      </form>
      <div v-if="selectedDeviceWarning" class="availability warning"><AlertCircle :size="16" />{{ selectedDeviceWarning }}</div>
      <div v-else-if="availability" class="availability" :class="{ ok: availability.available, warning: !availability.available }">
        <Check v-if="availability.available" :size="16" />
        <AlertCircle v-else :size="16" />
        {{ availability.available ? '该时段暂无已确认占用，可以提交预约' : `该时段存在 ${availability.conflictCount} 条已确认占用` }}
      </div>
      <div v-else-if="availabilityError" class="availability warning"><AlertCircle :size="16" />{{ availabilityError }}</div>
    </section>

    <div v-if="success" class="success-state">{{ success }}</div>
    <DataState :loading="loading || calendarLoading" :error="error || calendarError" :empty="filteredEvents.length === 0 && filteredReservations.length === 0" empty-text="暂无预约记录" />

    <section v-if="viewMode === 'timeline'" class="panel">
      <div class="panel-header">
        <h2>设备占用时间轴</h2>
        <span class="count">{{ selectedDayEvents.length }} 条当日占用</span>
      </div>
      <div class="timeline-head">
        <span>设备</span>
        <div class="ticks">
          <span>08:00</span>
          <span>11:30</span>
          <span>15:00</span>
          <span>18:30</span>
          <span>22:00</span>
        </div>
      </div>
      <div class="timeline-list">
        <div v-for="row in deviceRows" :key="row.device.id" class="timeline-row">
          <div class="timeline-device">
            <strong>{{ row.device.name }}</strong>
            <span>{{ row.device.id }} · {{ row.device.status }}</span>
          </div>
          <div class="timeline-track">
            <article
              v-for="item in row.events.filter((event) => toDateInput(new Date(event.startTime)) === selectedDate)"
              :key="item.id"
              class="timeline-block"
              :class="{ pending: item.status === '待审核', done: item.status === '已完成' }"
              :style="eventStyle(item)"
            >
              <strong>{{ item.reservationNo }}</strong>
              <span>{{ formatDateTime(item.startTime).slice(-11) }} - {{ formatDateTime(item.endTime).slice(-5) }}</span>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section v-else-if="viewMode === 'calendar'" class="panel">
      <div class="panel-header">
        <h2>周预约日历</h2>
        <span class="count">{{ filteredEvents.length }} 条范围内事件</span>
      </div>
      <div class="week-grid">
        <article v-for="day in weekDays" :key="day.key" class="week-day" :class="{ today: day.key === selectedDate }">
          <header><CalendarDays :size="16" />{{ day.label }}</header>
          <div class="day-events">
            <div v-for="item in eventsForDay(day.key)" :key="item.id" class="day-event">
              <strong>{{ item.deviceName }}</strong>
              <span>{{ item.reservationNo }} · {{ item.status }}</span>
              <small>{{ formatDateTime(item.startTime).slice(-11) }} - {{ formatDateTime(item.endTime).slice(-5) }}</small>
            </div>
            <p v-if="eventsForDay(day.key).length === 0">空闲</p>
          </div>
        </article>
      </div>
    </section>

    <section v-else class="panel">
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
              <td>{{ item.startAt ? formatDateTime(item.startAt) : item.slot }}</td>
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

.segmented {
  display: inline-flex;
  overflow: hidden;
  min-height: 36px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
}

.segmented button {
  min-width: 58px;
  border: 0;
  border-right: 1px solid var(--line);
  background: transparent;
  color: #40516a;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 800;
}

.segmented button:last-child {
  border-right: 0;
}

.segmented .active {
  background: #eaf4ff;
  color: var(--blue);
}

.reservation-form {
  grid-template-columns: repeat(4, minmax(150px, 1fr)) auto;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.availability {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px 16px;
  border: 1px solid #d9e4f1;
  border-radius: 8px;
  background: #f8fbff;
  color: #40516a;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 800;
}

.availability.ok {
  border-color: #bde8d7;
  background: #f0fbf6;
  color: #087849;
}

.availability.warning {
  border-color: #f7d7a3;
  background: #fff8ec;
  color: #9a5d00;
}

.timeline-head,
.timeline-row {
  display: grid;
  grid-template-columns: 230px minmax(520px, 1fr);
  gap: 14px;
  align-items: center;
}

.timeline-head {
  padding: 14px 18px 8px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.ticks {
  display: flex;
  justify-content: space-between;
}

.timeline-list {
  display: grid;
  gap: 10px;
  overflow-x: auto;
  padding: 0 18px 18px;
}

.timeline-row {
  min-height: 72px;
}

.timeline-device {
  display: grid;
  gap: 4px;
}

.timeline-device span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.timeline-track {
  position: relative;
  min-height: 48px;
  border: 1px solid #d9e4f1;
  border-radius: 8px;
  background: repeating-linear-gradient(90deg, #f8fbff 0 19.8%, #edf5fe 20% 20.2%);
}

.timeline-block {
  position: absolute;
  top: 7px;
  min-width: 92px;
  height: 34px;
  overflow: hidden;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--blue), var(--cyan));
  color: #fff;
  padding: 5px 8px;
  font-size: 11px;
  line-height: 1.1;
}

.timeline-block.pending {
  background: linear-gradient(135deg, var(--orange), #f7b733);
}

.timeline-block.done {
  background: linear-gradient(135deg, #9aa8ba, #6b7890);
}

.timeline-block strong,
.timeline-block span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(140px, 1fr));
  gap: 10px;
  overflow-x: auto;
  padding: 18px;
}

.week-day {
  min-height: 210px;
  border: 1px solid #d9e4f1;
  border-radius: 8px;
  background: #fbfdff;
}

.week-day.today {
  border-color: #9ec9ff;
  background: #f4f9ff;
}

.week-day header {
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 1px solid #edf2f7;
  padding: 10px;
  color: #40516a;
  font-size: 12px;
  font-weight: 800;
}

.day-events {
  display: grid;
  gap: 8px;
  padding: 10px;
}

.day-events p {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.day-event {
  border-left: 3px solid var(--blue);
  border-radius: 6px;
  background: #fff;
  padding: 8px;
  box-shadow: 0 8px 20px rgba(26, 57, 96, 0.08);
}

.day-event strong,
.day-event span,
.day-event small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.day-event span,
.day-event small {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

@media (max-width: 1180px) {
  .reservation-form {
    grid-template-columns: repeat(2, minmax(160px, 1fr));
  }

  .form-actions {
    grid-column: span 2;
  }
}

@media (max-width: 720px) {
  .reservation-form,
  .timeline-head,
  .timeline-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    grid-column: auto;
  }

  .timeline-head {
    display: none;
  }
}
</style>
