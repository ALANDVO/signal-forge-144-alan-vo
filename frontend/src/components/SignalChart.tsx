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

interface SignalChartProps {
  samples: number[];
  sampleRate: number;
  title: string;
  maxPoints?: number;
}

export function SignalChart({ samples, sampleRate, title, maxPoints = 1000 }: SignalChartProps) {
  const data = useMemo(() => {
    const step = Math.max(1, Math.floor(samples.length / maxPoints));
    const downsampled = samples.filter((_, i) => i % step === 0);
    const labels = downsampled.map((_, i) => (i * step / sampleRate).toFixed(4));
    return {
      labels,
      datasets: [
        {
          label: 'Amplitude',
          data: downsampled,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
        title: { display: true, text: 'Time (s)', color: '#64748b', font: { size: 12 } },
        grid: { color: '#e2e8f0' },
        ticks: { color: '#64748b', maxTicksLimit: 10 },
      },
      y: {
        title: { display: true, text: 'Amplitude', color: '#64748b', font: { size: 12 } },
        grid: { color: '#e2e8f0' },
        ticks: { color: '#64748b' },
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
