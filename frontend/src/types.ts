export interface SignalCreate {
  type: 'sine' | 'square' | 'sawtooth' | 'chirp' | 'noise' | 'custom';
  duration: number;
  sample_rate: number;
  frequency?: number;
  amplitude?: number;
  phase?: number;
  noise_type?: 'white' | 'pink' | 'brown';
  custom_samples?: number[];
  metadata?: Record<string, unknown>;
}

export interface SignalResponse {
  id: number;
  type: string;
  duration: number;
  sample_rate: number;
  frequency?: number;
  amplitude?: number;
  phase?: number;
  noise_type?: string;
  samples: number[];
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface SignalOperationResponse {
  id: number;
  signal_id: number;
  operation: string;
  parameters: Record<string, unknown>;
  created_at: string;
}

export interface FilterParams {
  filter_type: 'lowpass' | 'highpass' | 'bandpass';
  cutoff_freq: number;
  order?: number;
}

export interface PaginatedSignals {
  items: SignalResponse[];
  total: number;
  skip: number;
  limit: number;
}
