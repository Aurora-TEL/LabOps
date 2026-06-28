import { requestApi } from '@/api/client';
import { analyticsReport as mockAnalyticsReport } from '@/mock/analytics';
import type { AnalyticsReport } from '@/types';

interface BackendTrendPoint {
  date: string;
  value: number;
}

interface BackendStatusCount {
  status: string;
  count: number;
}

interface BackendCategoryCount {
  name: string;
  count: number;
}

interface BackendDeviceHealth {
  device_id: string;
  device_name: string;
  status: string;
  health_score: number;
}

interface BackendAnalyticsKpi {
  label: string;
  value: number;
  unit: string;
  delta: string;
  status: 'normal' | 'warning' | 'danger';
}

interface BackendAnalyticsReport {
  start_date: string;
  end_date: string;
  kpis: BackendAnalyticsKpi[];
  reservation_trend: BackendTrendPoint[];
  repair_trend: BackendTrendPoint[];
  reservation_status: BackendStatusCount[];
  fault_types: BackendCategoryCount[];
  maintenance_types: BackendCategoryCount[];
  device_health: BackendDeviceHealth[];
}

export interface AnalyticsLoadResult {
  data: AnalyticsReport;
  source: 'api' | 'mock';
  error?: string;
}

function mapReport(item: BackendAnalyticsReport): AnalyticsReport {
  return {
    startDate: item.start_date,
    endDate: item.end_date,
    kpis: item.kpis,
    reservationTrend: item.reservation_trend,
    repairTrend: item.repair_trend,
    reservationStatus: item.reservation_status,
    faultTypes: item.fault_types,
    maintenanceTypes: item.maintenance_types,
    deviceHealth: item.device_health.map((device) => ({
      deviceId: device.device_id,
      deviceName: device.device_name,
      status: device.status,
      healthScore: device.health_score
    }))
  };
}

export async function getOperationReport(params: { startDate: string; endDate: string }): Promise<AnalyticsLoadResult> {
  try {
    const search = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate
    });
    return {
      data: mapReport(await requestApi<BackendAnalyticsReport>(`/analytics/operation-report?${search.toString()}`)),
      source: 'api'
    };
  } catch (error) {
    return {
      data: mockAnalyticsReport,
      source: 'mock',
      error: error instanceof Error ? `${error.message}，已切换演示分析数据` : '分析接口暂不可用，已切换演示数据'
    };
  }
}
