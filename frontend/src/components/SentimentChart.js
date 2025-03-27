import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function SentimentChart({ positive, neutral, negative }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    // Clean up previous chart instance
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Create new chart
    const ctx = chartRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
          data: [positive, neutral, negative],
          backgroundColor: [
            'var(--bs-success)',
            'var(--bs-warning)',
            'var(--bs-danger)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const total = positive + neutral + negative;
                const percentage = Math.round((context.raw / total) * 100);
                return `${context.label}: ${context.raw} (${percentage}%)`;
              }
            }
          }
        }
      }
    });

    // Cleanup chart when component unmounts
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [positive, neutral, negative]);

  return (
    <div className="sentiment-chart-container">
      <canvas ref={chartRef} height="200"></canvas>
    </div>
  );
}

export default SentimentChart;
