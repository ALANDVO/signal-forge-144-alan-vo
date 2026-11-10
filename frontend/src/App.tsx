import { useState, useEffect } from 'react';
import { healthApi } from './api';
import { SignalForm } from './components/SignalForm';
import { SignalChart } from './components/SignalChart';
import { SpectrumChart } from './components/SpectrumChart';
import { SignalList } from './components/SignalList';
import { FilterPanel } from './components/FilterPanel';
import type { SignalResponse } from './types';

function App() {
  const [health, setHealth] = useState<{ status: string; service: string } | null>(null);
  const [dbHealth, setDbHealth] = useState<{ status: string; database: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSignal, setSelectedSignal] = useState<SignalResponse | null>(null);
  const [viewMode, setViewMode] = useState<'time' | 'frequency' | 'both'>('both');

  useEffect(() => {
    async function fetchHealth() {
      try {
        setLoading(true);
        const [healthRes, dbHealthRes] = await Promise.all([
          healthApi.check(),
          healthApi.db(),
        ]);
        setHealth(healthRes);
        setDbHealth(dbHealthRes);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
  }, []);

  const handleSignalCreated = (signal: SignalResponse) => {
    setSelectedSignal(signal);
  };

  const handleSelectSignal = (signal: SignalResponse) => {
    setSelectedSignal(signal);
  };

  const handleSignalUpdated = (signal: SignalResponse) => {
    setSelectedSignal(signal);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingCard}>
          <h1 style={styles.title}>Signal Forge</h1>
          <p style={styles.subtitle}>AI/ML Signal Processing Platform</p>
          <div style={styles.loading}>Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingCard}>
          <h1 style={styles.title}>Signal Forge</h1>
          <p style={{ ...styles.subtitle, color: '#dc2626' }}>Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.title}>Signal Forge</h1>
          <p style={styles.subtitle}>AI/ML Signal Processing Platform</p>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.statusBadge}>
            <span style={{
              ...styles.statusDot,
              backgroundColor: health?.status === 'healthy' ? '#22c55e' : '#ef4444',
            }} />
            <span style={styles.statusText}>
              {health?.status === 'healthy' ? 'API Healthy' : 'API Unhealthy'}
            </span>
          </div>
          <div style={styles.statusBadge}>
            <span style={{
              ...styles.statusDot,
              backgroundColor: dbHealth?.status === 'healthy' ? '#22c55e' : '#ef4444',
            }} />
            <span style={styles.statusText}>
              {dbHealth?.status === 'healthy' ? 'DB Connected' : 'DB Disconnected'}
            </span>
          </div>
        </div>
      </header>

      <main style={styles.main}>
        <aside style={styles.sidebar}>
          <SignalForm onSignalCreated={handleSignalCreated} />
          <SignalList onSelectSignal={handleSelectSignal} selectedSignalId={selectedSignal?.id ?? null} />
        </aside>

        <section style={styles.content}>
          {selectedSignal ? (
            <>
              <div style={styles.chartControls}>
                <h2 style={styles.chartTitle}>
                  {selectedSignal.type.charAt(0).toUpperCase() + selectedSignal.type.slice(1)} Signal
                  <span style={styles.signalMeta}>
                    #{selectedSignal.id} · {selectedSignal.duration.toFixed(3)}s @ {selectedSignal.sample_rate}Hz
                    {selectedSignal.frequency && ` · ${selectedSignal.frequency}Hz`}
                    {selectedSignal.noise_type && ` · ${selectedSignal.noise_type}`}
                  </span>
                </h2>
                <div style={styles.viewToggle}>
                  <button
                    onClick={() => setViewMode('time')}
                    style={{
                      ...styles.viewButton,
                      ...(viewMode === 'time' || viewMode === 'both' ? styles.viewButtonActive : {}),
                    }}
                  >
                    Time Domain
                  </button>
                  <button
                    onClick={() => setViewMode('frequency')}
                    style={{
                      ...styles.viewButton,
                      ...(viewMode === 'frequency' || viewMode === 'both' ? styles.viewButtonActive : {}),
                    }}
                  >
                    Frequency Domain
                  </button>
                  <button
                    onClick={() => setViewMode('both')}
                    style={{
                      ...styles.viewButton,
                      ...(viewMode === 'both' ? styles.viewButtonActive : {}),
                    }}
                  >
                    Both
                  </button>
                </div>
              </div>

              {(viewMode === 'time' || viewMode === 'both') && (
                <SignalChart
                  samples={selectedSignal.samples}
                  sampleRate={selectedSignal.sample_rate}
                  title="Time Domain"
                />
              )}

              {(viewMode === 'frequency' || viewMode === 'both') && (
                <SpectrumChart
                  samples={selectedSignal.samples}
                  sampleRate={selectedSignal.sample_rate}
                  title="Frequency Domain (FFT)"
                />
              )}
            </>
          ) : (
            <div style={styles.emptyState}>
              <div style={styles.emptyIcon}>📊</div>
              <h2 style={styles.emptyTitle}>No Signal Selected</h2>
              <p style={styles.emptyText}>
                Generate a new signal using the form on the left,
                or select an existing signal from the library.
              </p>
            </div>
          )}
        </section>

        <aside style={styles.sidebar}>
          <FilterPanel
            signal={selectedSignal}
            onSignalUpdated={handleSignalUpdated}
          />
        </aside>
      </main>

      <footer style={styles.footer}>
        <p>Signal Forge — Alan Vo · <a href="https://alanvo.net" target="_blank" rel="noopener noreferrer" style={styles.link}>alanvo.net</a> · <a href="https://x.com/alanvoasi" target="_blank" rel="noopener noreferrer" style={styles.link}>@alanvoasi</a></p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f8fafc',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: 'white',
    borderBottom: '1px solid #e2e8f0',
    position: 'sticky',
    top: 0,
    zIndex: 10,
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.375rem',
    padding: '0.375rem 0.75rem',
    backgroundColor: '#f1f5f9',
    borderRadius: '9999px',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#334155',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  statusText: {
    fontSize: '0.875rem',
  },
  title: {
    margin: '0 0 0.25rem',
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#1e293b',
  },
  subtitle: {
    margin: 0,
    fontSize: '0.875rem',
    color: '#64748b',
  },
  loadingCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '2rem',
    width: '100%',
    maxWidth: '600px',
    margin: '2rem auto',
  },
  loading: {
    color: '#64748b',
  },
  main: {
    flex: 1,
    display: 'grid',
    gridTemplateColumns: '320px 1fr 280px',
    gap: '1.5rem',
    padding: '1.5rem 2rem',
    maxWidth: '1600px',
    margin: '0 auto',
    width: '100%',
    boxSizing: 'border-box',
  },
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
    maxHeight: 'calc(100vh - 120px)',
    overflowY: 'auto',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
    minWidth: 0,
  },
  chartControls: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    flexWrap: 'wrap',
    gap: '1rem',
  },
  chartTitle: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1e293b',
  },
  signalMeta: {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 400,
    color: '#64748b',
    marginTop: '0.25rem',
  },
  viewToggle: {
    display: 'flex',
    gap: '0.5rem',
  },
  viewButton: {
    padding: '0.5rem 1rem',
    backgroundColor: 'white',
    color: '#334155',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '0.875rem',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  viewButtonActive: {
    backgroundColor: '#3b82f6',
    color: 'white',
    borderColor: '#3b82f6',
  },
  emptyState: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '3rem',
    textAlign: 'center',
    minHeight: '400px',
  },
  emptyIcon: {
    fontSize: '4rem',
    marginBottom: '1rem',
  },
  emptyTitle: {
    margin: '0 0 0.5rem',
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#1e293b',
  },
  emptyText: {
    margin: 0,
    fontSize: '1rem',
    color: '#64748b',
    maxWidth: '400px',
    lineHeight: 1.6,
  },
  footer: {
    marginTop: 'auto',
    padding: '1.5rem 2rem',
    borderTop: '1px solid #e2e8f0',
    backgroundColor: 'white',
    textAlign: 'center',
  },
  link: {
    color: '#3b82f6',
    textDecoration: 'none',
    fontWeight: 500,
  },
};

export default App;
