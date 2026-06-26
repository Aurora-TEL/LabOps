import { defineStore } from 'pinia';

import { getWorkbenchData } from '@/api/operations';
import { workbenchData } from '@/mock/operations';
import type { WorkbenchData } from '@/types';

export const useOperationsStore = defineStore('operations', {
  state: () => ({
    data: workbenchData as WorkbenchData,
    loading: false
  }),
  actions: {
    async load() {
      this.loading = true;
      try {
        this.data = await getWorkbenchData();
      } finally {
        this.loading = false;
      }
    }
  }
});
