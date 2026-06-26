<script setup lang="ts">
import { AlertCircle, Database, Loader2 } from 'lucide-vue-next';

defineProps<{
  loading?: boolean;
  error?: string;
  empty?: boolean;
  emptyText?: string;
}>();
</script>

<template>
  <div v-if="loading" class="data-state loading">
    <Loader2 :size="18" />
    <span>正在同步后端数据...</span>
  </div>
  <div v-else-if="error" class="data-state warning">
    <AlertCircle :size="18" />
    <span>{{ error }}</span>
  </div>
  <div v-else-if="empty" class="data-state">
    <Database :size="18" />
    <span>{{ emptyText || '暂无数据' }}</span>
  </div>
</template>
