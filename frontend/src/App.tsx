import { useState, useEffect } from 'react'

function App() {
  const [health, setHealth] = useState<{ status: string; service: string } | null>(null)
  const [dbHealth, setDbHealth] = useState<{ status: string; database: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchHealth() {
      try {
        setLoading(true)
        const [healthRes, dbHealthRes] = await Promise.all([
          fetch('/api/v1/health'),
          fetch('/api/v1/health/db'),
        ])
        const healthData = await healthRes.json()
        const dbHealthData = await dbHealthRes.json()
        setHealth(healthData)
        setDbHealth(dbHealthData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
  }, [])

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1 style={styles.title}>Signal Forge</h1>
          <p style={styles.subtitle}>AI/ML Signal Processing Platform</p>
          <div style={styles.loading}>Loading...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1 style={styles.title}>Signal Forge</h1>
          <p style={{ ...styles.subtitle, color: '#dc2626' }}>Error: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Signal Forge</h1>
        <p style={styles.subtitle}>AI/ML Signal Processing Platform</p>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>System Health</h2>
          <div style={styles.statusGrid}>
            <div style={{ ...styles.statusCard, backgroundColor: health?.status === 'healthy' ? '#dcfce7' : '#fee2e2' }}>
              <div style={styles.statusLabel}>API Status</div>
              <div style={{ ...styles.statusValue, color: health?.status === 'healthy' ? '#166534' : '#dc2626' }}>
                {health?.status ?? 'unknown'}
              </div>
            </div>
            <div style={{ ...styles.statusCard, backgroundColor: dbHealth?.status === 'healthy' ? '#dcfce7' : '#fee2e2' }}>
              <div style={styles.statusLabel}>Database</div>
              <div style={{ ...styles.statusValue, color: dbHealth?.status === 'healthy' ? '#166534' : '#dc2626' }}>
                {dbHealth?.database ?? 'unknown'}
              </div>
            </div>
          </div>
        </div>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Service Info</h2>
          <div style={styles.infoGrid}>
            <div style={styles.infoCard}>
              <div style={styles.infoLabel}>Service</div>
              <div style={styles.infoValue}>{health?.service ?? 'unknown'}</div>
            </div>
            <div style={styles.infoCard}>
              <div style={styles.infoLabel}>Version</div>
              <div style={styles.infoValue}>1.0.0</div>
            </div>
          </div>
        </div>

        <footer style={styles.footer}>
          <p>Signal Forge — Alan Vo | AI & Machine Learning</p>
        </footer>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    backgroundColor: '#f8fafc',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  card: {
    width: '100%',
    maxWidth: '600px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '2rem',
  },
  title: {
    margin: '0 0 0.5rem',
    fontSize: '2rem',
    fontWeight: 700,
    color: '#1e293b',
  },
  subtitle: {
    margin: '0 0 2rem',
    fontSize: '1rem',
    color: '#64748b',
  },
  loading: {
    color: '#64748b',
  },
  section: {
    marginBottom: '1.5rem',
  },
  sectionTitle: {
    margin: '0 0 1rem',
    fontSize: '1.125rem',
    fontWeight: 600,
    color: '#334155',
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
  },
  statusCard: {
    padding: '1rem',
    borderRadius: '8px',
  },
  statusLabel: {
    fontSize: '0.875rem',
    color: '#64748b',
    marginBottom: '0.25rem',
  },
  statusValue: {
    fontSize: '1.25rem',
    fontWeight: 600,
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
  },
  infoCard: {
    padding: '1rem',
    backgroundColor: '#f1f5f9',
    borderRadius: '8px',
  },
  infoLabel: {
    fontSize: '0.875rem',
    color: '#64748b',
    marginBottom: '0.25rem',
  },
  infoValue: {
    fontSize: '1.125rem',
    fontWeight: 600,
    color: '#1e293b',
  },
  footer: {
    marginTop: '2rem',
    paddingTop: '1rem',
    borderTop: '1px solid #e2e8f0',
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '0.875rem',
  },
}

export default App