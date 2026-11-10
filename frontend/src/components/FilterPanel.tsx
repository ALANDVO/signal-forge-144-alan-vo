import { useState, ChangeEvent } from 'react';
import { signalsApi } from '../api';
import type { SignalResponse } from '../types';

interface FilterPanelProps {
  signal: SignalResponse | null;
  onSignalUpdated: (signal: SignalResponse) => void;
}

export function FilterPanel({ signal, onSignalUpdated }: FilterPanelProps) {
  const [filterType, setFilterType] = useState<'lowpass' | 'highpass' | 'bandpass'>('lowpass');
  const [cutoffFreq, setCutoffFreq] = useState(1000);
  const [order, setOrder] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApplyFilter = async () => {
    if (!signal) return;

    setError(null);
    setLoading(true);

    try {
      const result = await signalsApi.filter(signal.id, {
        filter_type: filterType,
        cutoff_freq: cutoffFreq,
        order,
      });
      onSignalUpdated(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply filter');
    } finally {
      setLoading(false);
    }
  };

  const handleFFT = async () => {
    if (!signal) return;

    setError(null);
    setLoading(true);

    try {
      const result = await signalsApi.fft(signal.id);
      onSignalUpdated(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to compute FFT');
    } finally {
      setLoading(false);
    }
  };

  const maxFreq = signal ? signal.sample_rate / 2 : 22050;

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Signal Operations</h3>

      {signal && (
        <div style={styles.info}>
          <span>ID: {signal.id}</span>
          <span>{signal.type}</span>
          <span>{signal.duration.toFixed(3)}s</span>
          <span>{signal.sample_rate}Hz</span>
        </div>
      )}

      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>Digital Filter</h4>

        <div style={styles.field}>
          <label style={styles.label}>Filter Type</label>
          <select
            value={filterType}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => setFilterType(e.target.value as 'lowpass' | 'highpass' | 'bandpass')}
            style={styles.select}
          >
            <option value="lowpass">Lowpass</option>
            <option value="highpass">Highpass</option>
            <option value="bandpass">Bandpass</option>
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Cutoff Frequency (Hz)</label>
          <input
            type="number"
            value={cutoffFreq}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setCutoffFreq(parseFloat(e.target.value))}
            min="1"
            max={maxFreq}
            step="1"
            style={styles.input}
          />
          <small style={styles.hint}>Max: {maxFreq}Hz (Nyquist)</small>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Order</label>
          <input
            type="number"
            value={order}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setOrder(parseInt(e.target.value))}
            min="1"
            max="10"
            step="1"
            style={styles.input}
          />
        </div>

        <button onClick={handleApplyFilter} disabled={loading || !signal} style={styles.button}>
          {loading ? 'Applying...' : 'Apply Filter'}
        </button>
      </div>

      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>Frequency Analysis</h4>
        <button onClick={handleFFT} disabled={loading || !signal} style={styles.buttonSecondary}>
          {loading ? 'Computing...' : 'Compute FFT'}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    height: 'fit-content',
  },
  title: {
    margin: '0 0 1rem',
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1e293b',
  },
  info: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.75rem',
    marginBottom: '1rem',
    padding: '0.75rem',
    backgroundColor: '#f1f5f9',
    borderRadius: '8px',
    fontSize: '0.875rem',
    color: '#334155',
  },
  section: {
    marginBottom: '1.5rem',
  },
  sectionTitle: {
    margin: '0 0 1rem',
    fontSize: '1rem',
    fontWeight: 600,
    color: '#334155',
  },
  field: {
    marginBottom: '1rem',
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#334155',
  },
  input: {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '1rem',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '1rem',
    backgroundColor: 'white',
    boxSizing: 'border-box',
  },
  hint: {
    display: 'block',
    marginTop: '0.25rem',
    fontSize: '0.75rem',
    color: '#94a3b8',
  },
  button: {
    width: '100%',
    padding: '0.75rem 1rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    marginBottom: '0.5rem',
  },
  buttonSecondary: {
    width: '100%',
    padding: '0.75rem 1rem',
    backgroundColor: '#64748b',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
  error: {
    color: '#dc2626',
    fontSize: '0.875rem',
    marginTop: '1rem',
  },
};
