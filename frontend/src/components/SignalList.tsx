import { useState, useEffect, useCallback } from 'react';
import { signalsApi } from '../api';
import type { SignalResponse } from '../types';

interface SignalListProps {
  onSelectSignal: (signal: SignalResponse) => void;
  selectedSignalId: number | null;
}

export function SignalList({ onSelectSignal, selectedSignalId }: SignalListProps) {
  const [signals, setSignals] = useState<SignalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 10;

  const loadSignals = useCallback(async () => {
    try {
      setLoading(true);
      const data = await signalsApi.list(skip, limit);
      if (skip === 0) {
        setSignals(data);
      } else {
        setSignals(prev => [...prev, ...data]);
      }
      setHasMore(data.length === limit);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load signals');
    } finally {
      setLoading(false);
    }
  }, [skip]);

  useEffect(() => {
    loadSignals();
  }, [loadSignals]);

  const handleLoadMore = () => {
    setSkip(prev => prev + limit);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      sine: 'Sine',
      square: 'Square',
      sawtooth: 'Sawtooth',
      chirp: 'Chirp',
      noise: 'Noise',
      custom: 'Custom',
    };
    return labels[type] || type;
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Signal Library</h3>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.list}>
        {signals.length === 0 && !loading && (
          <div style={styles.empty}>No signals generated yet</div>
        )}

        {signals.map(signal => (
          <div
            key={signal.id}
            style={{
              ...styles.item,
              ...(selectedSignalId === signal.id ? styles.itemSelected : {}),
            }}
            onClick={() => onSelectSignal(signal)}
          >
            <div style={styles.itemHeader}>
              <span style={styles.itemType}>{getTypeLabel(signal.type)}</span>
              <span style={styles.itemId}>#{signal.id}</span>
            </div>
            <div style={styles.itemDetails}>
              <span>{signal.duration.toFixed(3)}s @ {signal.sample_rate}Hz</span>
              {signal.frequency && <span>{signal.frequency}Hz</span>}
              {signal.noise_type && <span>{signal.noise_type}</span>}
            </div>
            <div style={styles.itemDate}>{formatDate(signal.created_at)}</div>
          </div>
        ))}
      </div>

      {hasMore && (
        <button onClick={handleLoadMore} disabled={loading} style={styles.loadMore}>
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  title: {
    margin: '0 0 1rem',
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1e293b',
  },
  list: {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '1rem',
  },
  empty: {
    color: '#94a3b8',
    textAlign: 'center',
    padding: '2rem',
  },
  item: {
    padding: '0.75rem',
    borderRadius: '8px',
    cursor: 'pointer',
    border: '1px solid #e2e8f0',
    marginBottom: '0.5rem',
    transition: 'all 0.2s',
  },
  itemSelected: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  itemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.25rem',
  },
  itemType: {
    fontWeight: 600,
    color: '#1e293b',
    textTransform: 'capitalize',
  },
  itemId: {
    color: '#94a3b8',
    fontSize: '0.875rem',
  },
  itemDetails: {
    fontSize: '0.875rem',
    color: '#64748b',
    display: 'flex',
    gap: '1rem',
    marginBottom: '0.25rem',
  },
  itemDate: {
    fontSize: '0.75rem',
    color: '#94a3b8',
  },
  error: {
    color: '#dc2626',
    fontSize: '0.875rem',
    marginBottom: '1rem',
  },
  loadMore: {
    width: '100%',
    padding: '0.75rem',
    backgroundColor: '#f1f5f9',
    color: '#334155',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '1rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
};
