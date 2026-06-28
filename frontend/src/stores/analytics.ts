import { defineStore } from 'pinia';

import { getOperationReport } from '@/api/analytics';
import { analyticsReport } from '@/mock/analytics';
import type { AnalyticsReport } from '@/types';

function toDateInput(date: Date) {
  return date.toISOString().slice(0, 10);
}

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    report: analyticsReport as AnalyticsReport,
    loading: false,
    error: '',
    source: 'mock' as 'api' | 'mock',
    startDate: toDateInput(new Date(Date.now() - 29 * 24 * 60 * 60 * 1000)),
    endDate: toDateInput(new Date()),
    loaded: false,
    lastUpdated: ''
  }),
  actions: {
    async load() {
      this.loading = true;
      try {
        const result = await getOperationReport({ startDate: this.startDate, endDate: this.endDate });
        this.report = result.data;
        this.source = result.source;
        this.error = result.error ?? '';
        this.loaded = true;
        this.lastUpdated = new Date().toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      } finally {
        this.loading = false;
      }
    },
    async applyRange(startDate: string, endDate: string) {
      this.startDate = startDate;
      this.endDate = endDate;
      await this.load();
    }
  }
});
