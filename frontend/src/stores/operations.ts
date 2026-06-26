import { defineStore } from 'pinia';

import { getWorkbenchData } from '@/api/operations';
import { workbenchData } from '@/mock/operations';
import type { WorkbenchData } from '@/types';

export const useOperationsStore = defineStore('operations', {
  state: () => ({
    data: workbenchData as WorkbenchData,
    loading: false,
    error: '',
    source: 'mock' as 'api' | 'mock',
    loaded: false
  }),
  actions: {
    async load() {
      this.loading = true;
      try {
        const result = await getWorkbenchData();
        this.data = result.data;
        this.source = result.source;
        this.error = result.error ?? '';
        this.loaded = true;
      } finally {
        this.loading = false;
      }
    },
    async refresh() {
      await this.load();
    }
  }
});
