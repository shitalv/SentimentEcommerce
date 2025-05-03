import React, { useState, useEffect } from 'react';

function SentimentTrendChart({ productId }) {
  const [trendData, setTrendData] = useState([]);
  const [trendMetrics, setTrendMetrics] = useState({});
  const [timeRange, setTimeRange] = useState('month');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch trend data when component mounts or productId changes
    const fetchTrendData = async () => {
      setIsLoading(true);
      try {
        let url = `/api/sentiment-trends?time_range=${timeRange}`;
        if (productId) {
          url += `&product_id=${productId}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setTrendData(data.trend_data || []);
        setTrendMetrics(data.trend_metrics || {});
        setError(null);
      } catch (err) {
        console.error('Error fetching sentiment trend data:', err);
        setError('Failed to load sentiment trend data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTrendData();
  }, [productId, timeRange]);
  
  // Helper function to generate trend indicator
  const renderTrendIndicator = () => {
    if (!trendMetrics || trendMetrics.insufficient_data) {
      return (
        <div className="badge bg-secondary">
          <i className="fas fa-question-circle me-1"></i>
          Insufficient Data
        </div>
      );
    }
    
    let badgeClass = "bg-secondary";
    let icon = "fa-minus";
    let label = "Stable";
    
    if (trendMetrics.trend_direction > 0) {
      badgeClass = "bg-success";
      icon = "fa-arrow-up";
      label = "Improving";
    } else if (trendMetrics.trend_direction < 0) {
      badgeClass = "bg-danger";
      icon = "fa-arrow-down";
      label = "Declining";
    }
    
    return (
      <div className={`badge ${badgeClass}`}>
        <i className={`fas ${icon} me-1`}></i>
        {label} ({Math.abs(trendMetrics.trend_percent || 0)}%)
      </div>
    );
  };
  
  // Render chart based on data
  const renderChart = () => {
    if (isLoading) {
      return <div className="text-center py-4"><div className="spinner-border"></div></div>;
    }
    
    if (error) {
      return <div className="alert alert-danger">{error}</div>;
    }
    
    if (!trendData || trendData.length === 0) {
      return (
        <div className="alert alert-info">
          No trend data available. This could be because there are not enough dated reviews to analyze.
        </div>
      );
    }
    
    // Reverse data to show chronological order
    const reversedData = [...trendData].reverse();
    
    // Calculate max value for chart height
    const maxValue = Math.max(
      ...reversedData.flatMap(item => [
        item.positive_percent || 0,
        item.neutral_percent || 0,
        item.negative_percent || 0
      ])
    );
    
    // Chart height in pixels
    const chartHeight = 200;
    
    return (
      <div className="trend-chart mt-3">
        <div className="chart-bars d-flex align-items-end" style={{ height: `${chartHeight}px` }}>
          {reversedData.map((period, index) => (
            <div key={index} className="period-bar mx-1 position-relative" style={{ flex: 1 }}>
              <div className="bar-negative" 
                style={{ 
                  height: `${(period.negative_percent / 100) * chartHeight}px`,
                  backgroundColor: '#dc3545'
                }}>
              </div>
              <div className="bar-neutral" 
                style={{ 
                  height: `${(period.neutral_percent / 100) * chartHeight}px`,
                  backgroundColor: '#6c757d'
                }}>
              </div>
              <div className="bar-positive" 
                style={{ 
                  height: `${(period.positive_percent / 100) * chartHeight}px`,
                  backgroundColor: '#198754'
                }}>
              </div>
              <div className="period-label position-absolute bottom-0 start-50 translate-middle-x mt-1 small" 
                style={{ transform: 'translateY(100%)' }}>
                {period.period}
              </div>
            </div>
          ))}
        </div>
        
        <div className="chart-legend d-flex justify-content-center mt-4">
          <div className="legend-item me-3">
            <span className="badge" style={{ backgroundColor: '#198754', width: '20px', height: '10px', display: 'inline-block' }}></span>
            <span className="ms-1">Positive</span>
          </div>
          <div className="legend-item me-3">
            <span className="badge" style={{ backgroundColor: '#6c757d', width: '20px', height: '10px', display: 'inline-block' }}></span>
            <span className="ms-1">Neutral</span>
          </div>
          <div className="legend-item">
            <span className="badge" style={{ backgroundColor: '#dc3545', width: '20px', height: '10px', display: 'inline-block' }}></span>
            <span className="ms-1">Negative</span>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="card mb-4">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">
          <i className="fas fa-chart-line me-2"></i>
          Time-Based Sentiment Trends
        </h5>
      </div>
      <div className="card-body">
        <p className="lead">
          Track how customer sentiment has changed over time for this product.
        </p>
        
        <div className="d-flex justify-content-between align-items-center mb-3">
          <div className="btn-group" role="group">
            <button 
              type="button" 
              className={`btn btn-sm ${timeRange === 'month' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setTimeRange('month')}
            >
              Monthly
            </button>
            <button 
              type="button" 
              className={`btn btn-sm ${timeRange === 'week' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setTimeRange('week')}
            >
              Weekly
            </button>
            <button 
              type="button" 
              className={`btn btn-sm ${timeRange === 'day' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setTimeRange('day')}
            >
              Daily
            </button>
          </div>
          
          <div className="trend-indicator">
            <span className="me-2">Trend:</span>
            {renderTrendIndicator()}
          </div>
        </div>
        
        {renderChart()}
        
        {!isLoading && trendData && trendData.length > 0 && (
          <div className="mt-3 text-muted small">
            Based on {trendData.reduce((sum, period) => sum + period.review_count, 0)} reviews over {trendData.length} {trendData[0].period_name}s.
          </div>
        )}
      </div>
    </div>
  );
}

export default SentimentTrendChart;