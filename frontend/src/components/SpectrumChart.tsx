import { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface SpectrumChartProps {
  samples: number[];
  sampleRate: number;
  title: string;
  maxPoints?: number;
}

export function SpectrumChart({ samples, sampleRate, title, maxPoints = 500 }: SpectrumChartProps) {
  const data = useMemo(() => {
    const n = samples.length;
    const fftSize = Math.min(1 << Math.ceil(Math.log2(n)), n);
    const real = new Float64Array(fftSize);
    const imag = new Float64Array(fftSize);

    for (let i = 0; i < fftSize; i++) {
      real[i] = samples[i];
    }

    // Simple FFT implementation (Cooley-Tukey)
    function fft(real: Float64Array, imag: Float64Array): void {
      const n = real.length;
      if (n <= 1) return;

      // Bit-reversal permutation
      let j = 0;
      for (let i = 1; i < n; i++) {
        let bit = n >> 1;
        while (j & bit) {
          j ^= bit;
          bit >>= 1;
        }
        j ^= bit;
        if (i < j) {
          [real[i], real[j]] = [real[j], real[i]];
          [imag[i], imag[j]] = [imag[j], imag[i]];
        }
      }

      // Cooley-Tukey
      for (let len = 2; len <= n; len <<= 1) {
        const angle = -2 * Math.PI / len;
        const wlenReal = Math.cos(angle);
        const wlenImag = Math.sin(angle);
        for (let i = 0; i < n; i += len) {
          let wReal = 1;
          let wImag = 0;
          for (let j = 0; j < len / 2; j++) {
            const uReal = real[i + j];
            const uImag = imag[i + j];
            const vReal = real[i + j + len / 2] * wReal - imag[i + j + len / 2] * wImag;
            const vImag = real[i + j + len / 2] * wImag + imag[i + j + len / 2] * wReal;
            real[i + j] = uReal + vReal;
            imag[i + j] = uImag + vImag;
            real[i + j + len / 2] = uReal - vReal;
            imag[i + j + len / 2] = uImag - vImag;
            const nextWReal = wReal * wlenReal - wImag * wlenImag;
            const nextWImag = wReal * wlenImag + wImag * wlenReal;
            wReal = nextWReal;
            wImag = nextWImag;
          }
        }
      }
    }

    fft(real, imag);

    const magnitudes = new Float64Array(fftSize / 2);
    for (let i = 0; i < fftSize / 2; i++) {
      magnitudes[i] = Math.sqrt(real[i] * real[i] + imag[i] * imag[i]);
    }

    // Convert to dB
    const maxMag = Math.max(...magnitudes);
    const dbValues = Array.from(magnitudes).map(m => 
      m > 0 ? 20 * Math.log10(m / maxMag) : -100
    );

    const step = Math.max(1, Math.floor(dbValues.length / maxPoints));
    const downsampled = dbValues.filter((_, i) => i % step === 0);
    const labels = downsampled.map((_, i) => {
      const freq = (i * step * sampleRate) / fftSize;
      return freq.toFixed(1);
    });

    return {
      labels,
      datasets: [
        {
          label: 'Magnitude (dB)',
          data: downsampled,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.1,
          pointRadius: 0,
          borderWidth: 1.5,
        },
      ],
    };
  }, [samples, sampleRate, maxPoints]);

  const options: ChartOptions<'line'> = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: title,
        font: { size: 14, weight: 'bold' },
        color: '#1e293b',
      },
      legend: { display: false },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Frequency (Hz)', color: '#64748b', font: { size: 12 } },
        grid: { color: '#e2e8f0' },
        ticks: { color: '#64748b', maxTicksLimit: 10 },
        type: 'linear' as const,
      },
      y: {
        title: { display: true, text: 'Magnitude (dB)', color: '#64748b', font: { size: 12 } },
        grid: { color: '#e2e8f0' },
        ticks: { color: '#64748b' },
        suggestedMin: -100,
        suggestedMax: 0,
      },
    },
    interaction: { mode: 'nearest' as const, axis: 'x' as const, intersect: false },
  }), [title]);

  return (
    <div style={styles.container}>
      <Line data={data} options={options} />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    minHeight: '300px',
  },
};
