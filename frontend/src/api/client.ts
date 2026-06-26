interface ApiResponse<T> {
  code?: number;
  message?: string;
  data?: T;
}

export interface PageData<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = (configuredBaseUrl || '/api/v1').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function requestApi<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: 'application/json',
      ...init?.headers
    },
    ...init
  });

  if (!response.ok) {
    throw new ApiError(`接口请求失败：${response.status} ${response.statusText}`, response.status);
  }

  const payload = (await response.json()) as ApiResponse<T>;

  if (typeof payload.code === 'number' && payload.code !== 0) {
    throw new ApiError(payload.message || '接口返回业务错误', payload.code);
  }

  return payload.data as T;
}
