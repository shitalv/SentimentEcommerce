import React, { useState, useEffect } from 'react';

function ProductRecommendations({ productId, onSelectProduct }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Only fetch if we have a product ID
    if (productId) {
      fetchRecommendations();
    }
  }, [productId]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/products/${productId}/recommendations?limit=4`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }
      
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Unable to load recommendations');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (scores) => {
    if (!scores) return 'secondary';
    
    // Calculate the dominant sentiment
    const total = scores.positive + scores.neutral + scores.negative;
    
    if (total === 0) return 'secondary';
    
    if (scores.positive > scores.negative && scores.positive > scores.neutral) {
      return 'success';
    } else if (scores.negative > scores.positive && scores.negative > scores.neutral) {
      return 'danger';
    } else {
      return 'warning';
    }
  };
  
  const truncateText = (text, maxLength = 50) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Similar Products Based on Sentiment</h5>
        </div>
        <div className="card-body text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Analyzing sentiment patterns...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Similar Products Based on Sentiment</h5>
        </div>
        <div className="card-body text-center py-4">
          <div className="alert alert-warning mb-0" role="alert">
            <i className="fas fa-exclamation-triangle me-2"></i>
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Similar Products Based on Sentiment</h5>
        </div>
        <div className="card-body text-center py-4">
          <i className="fas fa-info-circle fa-2x mb-3 text-muted"></i>
          <p>No recommendations available for this product.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card mb-4">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="fas fa-thumbs-up me-2"></i>
          Recommended Products Based on Sentiment Analysis
        </h5>
      </div>
      <div className="card-body">
        <p className="text-muted mb-4">
          These recommendations are powered by our sentiment analysis engine, 
          finding products with similar positive sentiment patterns.
        </p>
        
        <div className="row">
          {recommendations.map((product) => (
            <div className="col-md-6 col-lg-3 mb-4" key={product.id}>
              <div className="card h-100 recommendation-card">
                <div className="card-header text-center bg-light">
                  <span className={`badge bg-${getSentimentColor(product.sentiment_scores)} position-absolute top-0 end-0 mt-2 me-2`}>
                    <i className="fas fa-chart-line me-1"></i>
                    {(product.sentiment_scores?.positive || 0).toFixed(1)}
                  </span>
                  <svg className="bd-placeholder-img card-img-top" width="100%" height="120" xmlns="http://www.w3.org/2000/svg" role="img" preserveAspectRatio="xMidYMid slice" focusable="false">
                    <title>{product.name}</title>
                    <rect width="100%" height="100%" fill="#55595c"/>
                    <text x="50%" y="50%" fill="#eceeef" dy=".3em">{product.name.substring(0, 10)}</text>
                  </svg>
                </div>
                <div className="card-body d-flex flex-column">
                  <h6 className="card-title mb-2">{product.name}</h6>
                  <p className="card-text small text-muted mb-3">{truncateText(product.description, 60)}</p>
                  <div className="mt-auto">
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="badge bg-secondary">{product.category}</span>
                      <span className="price">${(product.price || 0).toFixed(2)}</span>
                    </div>
                    <button 
                      className="btn btn-outline-primary btn-sm w-100 mt-2"
                      onClick={() => onSelectProduct(product.id)}
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ProductRecommendations;