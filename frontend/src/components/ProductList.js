import React from 'react';

function ProductList({ products, onSelectProduct }) {
  const getSentimentClass = (score) => {
    if (score >= 0.5) return 'sentiment-positive';
    if (score >= 0.3) return 'sentiment-neutral';
    return 'sentiment-negative';
  };

  const getSentimentBadge = (score) => {
    if (score >= 0.5) {
      return (
        <span className="badge bg-success sentiment-badge">
          <i className="fas fa-thumbs-up me-1"></i>
          Positive
        </span>
      );
    } else if (score >= 0.3) {
      return (
        <span className="badge bg-warning text-dark sentiment-badge">
          <i className="fas fa-balance-scale me-1"></i>
          Neutral
        </span>
      );
    } else {
      return (
        <span className="badge bg-danger sentiment-badge">
          <i className="fas fa-thumbs-down me-1"></i>
          Negative
        </span>
      );
    }
  };

  const renderProductCards = () => {
    if (products.length === 0) {
      return (
        <div className="col-12 text-center py-5">
          <i className="fas fa-search fa-3x mb-3 text-secondary"></i>
          <h3>No products found</h3>
          <p className="text-muted">Try adjusting your search or filter criteria</p>
        </div>
      );
    }

    return products.map(product => (
      <div key={product.id} className="col-md-4 mb-4">
        <div className="card h-100 position-relative">
          {getSentimentBadge(product.sentiment_score)}
          <div className="product-img-container bg-light p-3">
            <svg className="bd-placeholder-img card-img-top" width="100%" height="150" xmlns="http://www.w3.org/2000/svg" role="img" preserveAspectRatio="xMidYMid slice" focusable="false">
              <title>{product.name}</title>
              <rect width="100%" height="100%" fill="#55595c"/>
              <text x="50%" y="50%" fill="#eceeef" dy=".3em">{product.name}</text>
            </svg>
          </div>
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="badge bg-secondary">{product.category}</span>
              <div className={`${getSentimentClass(product.sentiment_score)}`}>
                <i className="fas fa-star me-1"></i>
                <strong>{product.sentiment_score.toFixed(2)}</strong>
              </div>
            </div>
            <h5 className="card-title">{product.name}</h5>
            <p className="card-text text-truncate">{product.description}</p>
            <div className="d-flex justify-content-between align-items-center">
              <span className="h5 mb-0">${product.price.toFixed(2)}</span>
              <button 
                className="btn btn-primary"
                onClick={() => onSelectProduct(product.id)}
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    ));
  };

  return (
    <div className="row">
      {renderProductCards()}
    </div>
  );
}

export default ProductList;
