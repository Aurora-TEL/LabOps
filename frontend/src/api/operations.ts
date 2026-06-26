import { workbenchData } from '@/mock/operations';
import type { WorkbenchData } from '@/types';

export function getWorkbenchData(): Promise<WorkbenchData> {
  return Promise.resolve(workbenchData);
}
