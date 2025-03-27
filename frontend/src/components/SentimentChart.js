import React, { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';

function SentimentChart({ positive, neutral, negative, product }) {
  const donutChartRef = useRef(null);
  const heatmapChartRef = useRef(null);
  const donutChartInstance = useRef(null);
  const heatmapChartInstance = useRef(null);
  const [activeTab, setActiveTab] = useState('donut');

  // Generate heatmap data from reviews if available - Amazon style
  const generateHeatmapData = () => {
    if (!product || !product.reviews) return null;
    
    // Sort reviews by date (if available) to show trends over time
    const sortedReviews = [...product.reviews];
    if (sortedReviews[0].date) {
      sortedReviews.sort((a, b) => {
        // Try to parse dates, fall back to original order if can't parse
        try {
          return new Date(a.date) - new Date(b.date);
        } catch (e) {
          return 0;
        }
      });
    }
    
    // Extract review sentiment data - Amazon style heatmap (more granular)
    return sortedReviews.map((review, index) => {
      const sentiment = review.sentiment || 0.5; // Default to neutral if not available
      let color;
      
      // Amazon star-like coloring (5 levels)
      if (sentiment >= 0.8) color = 'rgba(0, 128, 0, 0.95)';       // 5 stars (dark green)
      else if (sentiment >= 0.6) color = 'rgba(40, 167, 69, 0.8)';  // 4 stars (green)
      else if (sentiment >= 0.4) color = 'rgba(255, 193, 7, 0.8)';  // 3 stars (yellow)
      else if (sentiment >= 0.2) color = 'rgba(255, 128, 0, 0.8)';  // 2 stars (orange)
      else color = 'rgba(220, 53, 69, 0.8)';                        // 1 star (red)
      
      // Extract keywords for tooltip
      const keywordText = review.keywords && review.keywords.length > 0 
        ? review.keywords.slice(0, 3).map(k => k.keyword).join(', ')
        : 'No specific keywords';
      
      return {
        x: index,
        y: 0,
        v: sentiment,
        color: color,
        reviewText: review.text.substring(0, 60) + (review.text.length > 60 ? '...' : ''),
        author: review.author || 'Anonymous',
        date: review.date || 'Unknown date',
        keywords: keywordText,
        // Calculate a star rating equivalent (Amazon style)
        stars: Math.round(sentiment * 5 * 10) / 10
      };
    });
  };

  useEffect(() => {
    // Clean up previous chart instances
    if (donutChartInstance.current) {
      donutChartInstance.current.destroy();
    }
    
    // Create new donut chart
    const donutCtx = donutChartRef.current.getContext('2d');
    donutChartInstance.current = new Chart(donutCtx, {
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
          title: {
            display: true,
            text: 'Sentiment Distribution',
            font: {
              size: 16
            }
          },
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

    // Create heatmap chart if we have a product with reviews
    if (heatmapChartRef.current && product && product.reviews) {
      const heatmapData = generateHeatmapData();
      
      if (heatmapChartInstance.current) {
        heatmapChartInstance.current.destroy();
      }
      
      if (heatmapData && heatmapData.length > 0) {
        const heatmapCtx = heatmapChartRef.current.getContext('2d');
        
        // Custom chart for heatmap-like visualization
        heatmapChartInstance.current = new Chart(heatmapCtx, {
          type: 'bar',
          data: {
            labels: heatmapData.map((d, i) => `Review ${i+1}`),
            datasets: [{
              label: 'Sentiment Score',
              data: heatmapData.map(d => d.v),
              backgroundColor: heatmapData.map(d => d.color),
              borderColor: 'rgba(0, 0, 0, 0.1)',
              borderWidth: 1,
              barThickness: 30
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: 'Amazon Review Sentiment Heatmap Analysis',
                font: {
                  size: 16
                }
              },
              subtitle: {
                display: true,
                text: 'Hover over bars to see review details and extracted keywords',
                font: {
                  size: 12,
                  style: 'italic'
                },
                padding: {
                  bottom: 10
                }
              },
              tooltip: {
                callbacks: {
                  title: function(tooltipItems) {
                    const index = tooltipItems[0].dataIndex;
                    return `${heatmapData[index].author} (${heatmapData[index].date})`;
                  },
                  label: function(context) {
                    const index = context.dataIndex;
                    const score = Math.round(heatmapData[index].v * 100) / 100;
                    let sentiment = 'Neutral';
                    if (score >= 0.5) sentiment = 'Positive';
                    if (score < 0.3) sentiment = 'Negative';
                    
                    // Amazon style stars rating
                    const stars = heatmapData[index].stars;
                    const starDisplay = '★'.repeat(Math.floor(stars)) + (stars % 1 >= 0.5 ? '½' : '');
                    
                    return [
                      `Amazon Rating: ${starDisplay} (${stars}/5)`,
                      `Sentiment: ${sentiment} (${score})`, 
                      `Key aspects: ${heatmapData[index].keywords}`,
                      `"${heatmapData[index].reviewText}"`
                    ];
                  }
                }
              },
              legend: {
                display: false
              }
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Sentiment Score (0-1)'
                },
                min: 0,
                max: 1,
              },
              y: {
                ticks: {
                  display: true
                }
              }
            }
          }
        });
      }
    }

    // Cleanup charts when component unmounts
    return () => {
      if (donutChartInstance.current) {
        donutChartInstance.current.destroy();
      }
      if (heatmapChartInstance.current) {
        heatmapChartInstance.current.destroy();
      }
    };
  }, [positive, neutral, negative, product, activeTab]);

  return (
    <div className="sentiment-chart-container mb-4">
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'donut' ? 'active' : ''}`} 
            onClick={() => setActiveTab('donut')}
          >
            Sentiment Distribution
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'heatmap' ? 'active' : ''}`}
            onClick={() => setActiveTab('heatmap')}
            disabled={!product || !product.reviews}
          >
            Amazon Review Heatmap
          </button>
        </li>
      </ul>
      
      <div className={`chart-container ${activeTab === 'donut' ? 'd-block' : 'd-none'}`}>
        <canvas ref={donutChartRef} height="200"></canvas>
      </div>
      
      <div className={`chart-container ${activeTab === 'heatmap' ? 'd-block' : 'd-none'}`}>
        <canvas ref={heatmapChartRef} height={product && product.reviews ? Math.max(200, product.reviews.length * 40) : 200}></canvas>
      </div>
    </div>
  );
}

export default SentimentChart;
