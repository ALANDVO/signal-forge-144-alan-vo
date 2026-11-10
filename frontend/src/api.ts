import type { SignalCreate, SignalResponse, SignalOperationResponse, FilterParams } from './types';

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const signalsApi = {
  create: (signal: SignalCreate) =>
    request<SignalResponse>('/signals', {
      method: 'POST',
      body: JSON.stringify(signal),
    }),

  list: (skip = 0, limit = 100) =>
    request<SignalResponse[]>(`/signals?skip=${skip}&limit=${limit}`),

  get: (id: number) =>
    request<SignalResponse>(`/signals/${id}`),

  fft: (id: number) =>
    request<SignalResponse>(`/signals/${id}/fft`, { method: 'POST' }),

  filter: (id: number, params: FilterParams) =>
    request<SignalResponse>(`/signals/${id}/filter`, {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  convolve: (signalId: number, kernelId: number) =>
    request<SignalResponse>(`/signals/${signalId}/convolve?kernel_id=${kernelId}`, {
      method: 'POST',
    }),

  operations: (id: number) =>
    request<SignalOperationResponse[]>(`/signals/${id}/operations`),
};

export const healthApi = {
  check: () => request<{ status: string; service: string }>('/health'),
  db: () => request<{ status: string; database: string }>('/health/db'),
};
