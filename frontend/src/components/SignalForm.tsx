import { useState, ChangeEvent } from 'react';
import { signalsApi } from '../api';
import type { SignalCreate } from '../types';

interface SignalFormProps {
  onSignalCreated: (signal: any) => void;
}

export function SignalForm({ onSignalCreated }: SignalFormProps) {
  const [signalType, setSignalType] = useState<SignalCreate['type']>('sine');
  const [duration, setDuration] = useState(1);
  const [sampleRate, setSampleRate] = useState(44100);
  const [frequency, setFrequency] = useState(440);
  const [amplitude, setAmplitude] = useState(1);
  const [phase, setPhase] = useState(0);
  const [noiseType, setNoiseType] = useState<'white' | 'pink' | 'brown'>('white');
  const [customSamples, setCustomSamples] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const signal: SignalCreate = {
        type: signalType,
        duration,
        sample_rate: sampleRate,
      };

      if (['sine', 'square', 'sawtooth', 'chirp'].includes(signalType)) {
        signal.frequency = frequency;
        signal.amplitude = amplitude;
        signal.phase = phase;
      }

      if (signalType === 'noise') {
        signal.noise_type = noiseType;
        signal.amplitude = amplitude;
      }

      if (signalType === 'custom') {
        const samples = customSamples.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
        if (samples.length === 0) {
          throw new Error('Custom signal requires at least one sample value');
        }
        signal.custom_samples = samples;
        signal.duration = samples.length / sampleRate;
      }

      const result = await signalsApi.create(signal);
      onSignalCreated(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create signal');
    } finally {
      setLoading(false);
    }
  };

  const showFrequency = ['sine', 'square', 'sawtooth', 'chirp'].includes(signalType);
  const showNoiseType = signalType === 'noise';
  const showCustom = signalType === 'custom';

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3 style={styles.title}>Generate Signal</h3>

      <div style={styles.field}>
        <label style={styles.label}>Signal Type</label>
        <select
          value={signalType}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => setSignalType(e.target.value as SignalCreate['type'])}
          style={styles.select}
        >
          <option value="sine">Sine Wave</option>
          <option value="square">Square Wave</option>
          <option value="sawtooth">Sawtooth Wave</option>
          <option value="chirp">Chirp</option>
          <option value="noise">Noise</option>
          <option value="custom">Custom Samples</option>
        </select>
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Duration (seconds)</label>
        <input
          type="number"
          value={duration}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setDuration(parseFloat(e.target.value))}
          min="0.001"
          max="10"
          step="0.001"
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Sample Rate (Hz)</label>
        <input
          type="number"
          value={sampleRate}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setSampleRate(parseInt(e.target.value))}
          min="1000"
          max="192000"
          step="1000"
          style={styles.input}
        />
      </div>

      {showFrequency && (
        <>
          <div style={styles.field}>
            <label style={styles.label}>Frequency (Hz)</label>
            <input
              type="number"
              value={frequency}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setFrequency(parseFloat(e.target.value))}
              min="0.1"
              max="20000"
              step="0.1"
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Amplitude</label>
            <input
              type="number"
              value={amplitude}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setAmplitude(parseFloat(e.target.value))}
              min="0"
              max="10"
              step="0.1"
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Phase (radians)</label>
            <input
              type="number"
              value={phase}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPhase(parseFloat(e.target.value))}
              min="0"
              max={2 * Math.PI}
              step="0.01"
              style={styles.input}
            />
          </div>
        </>
      )}

      {showNoiseType && (
        <div style={styles.field}>
          <label style={styles.label}>Noise Type</label>
          <select
            value={noiseType}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => setNoiseType(e.target.value as 'white' | 'pink' | 'brown')}
            style={styles.select}
          >
            <option value="white">White Noise</option>
            <option value="pink">Pink Noise</option>
            <option value="brown">Brown Noise</option>
          </select>
        </div>
      )}

      {showNoiseType && (
        <div style={styles.field}>
          <label style={styles.label}>Amplitude</label>
          <input
            type="number"
            value={amplitude}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setAmplitude(parseFloat(e.target.value))}
            min="0"
            max="10"
            step="0.1"
            style={styles.input}
          />
        </div>
      )}

      {showCustom && (
        <div style={styles.field}>
          <label style={styles.label}>Custom Samples (comma-separated)</label>
          <textarea
            value={customSamples}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setCustomSamples(e.target.value)}
            rows={3}
            placeholder="0.1, 0.5, -0.3, 0.8, ..."
            style={{ ...styles.input, fontFamily: 'monospace' }}
          />
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}

      <button type="submit" disabled={loading} style={styles.button}>
        {loading ? 'Generating...' : 'Generate Signal'}
      </button>
    </form>
  );
}

const styles: Record<string, React.CSSProperties> = {
  form: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
  },
  title: {
    margin: '0 0 1.5rem',
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1e293b',
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
  error: {
    color: '#dc2626',
    fontSize: '0.875rem',
    marginBottom: '1rem',
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
    transition: 'background-color 0.2s',
  },
};
