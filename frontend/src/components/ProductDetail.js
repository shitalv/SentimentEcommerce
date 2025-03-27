import React from 'react';
import SentimentChart from './SentimentChart';
import HypeVsRealityCheck from './HypeVsRealityCheck';

function ProductDetail({ product, onBack }) {
  const getSentimentClass = (score) => {
    if (score >= 0.5) return 'sentiment-positive';
    if (score >= 0.3) return 'sentiment-neutral';
    return 'sentiment-negative';
  };

  const getSentimentIcon = (score) => {
    if (score >= 0.5) return <i className="fas fa-thumbs-up me-1"></i>;
    if (score >= 0.3) return <i className="fas fa-balance-scale me-1"></i>;
    return <i className="fas fa-thumbs-down me-1"></i>;
  };

  const getReviewClass = (sentiment) => {
    if (sentiment >= 0.5) return 'review-positive';
    if (sentiment >= 0.3) return 'review-neutral';
    return 'review-negative';
  };

  return (
    <div>
      <button className="btn btn-outline-secondary mb-4" onClick={onBack}>
        <i className="fas fa-arrow-left me-2"></i>Back to Products
      </button>
      
      <div className="row">
        <div className="col-md-5">
          <div className="card mb-4">
            <div className="product-img-container bg-light p-3">
              <svg className="bd-placeholder-img card-img-top" width="100%" height="300" xmlns="http://www.w3.org/2000/svg" role="img" preserveAspectRatio="xMidYMid slice" focusable="false">
                <title>{product.name}</title>
                <rect width="100%" height="100%" fill="#55595c"/>
                <text x="50%" y="50%" fill="#eceeef" dy=".3em">{product.name}</text>
              </svg>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="badge bg-secondary">{product.category}</span>
                <div className={`${getSentimentClass(product.sentiment_score)}`}>
                  {getSentimentIcon(product.sentiment_score)}
                  <strong>Sentiment: {product.sentiment_score.toFixed(2)}</strong>
                </div>
              </div>
              <h3 className="card-title">{product.name}</h3>
              <p className="h4 mb-3">${product.price.toFixed(2)}</p>
              <p className="card-text">{product.description}</p>
              <button className="btn btn-primary">
                <i className="fas fa-shopping-cart me-2"></i>Add to Cart
              </button>
            </div>
          </div>
        </div>
        
        <div className="col-md-7">
          <div className="card mb-4">
            <div className="card-header">
              <h4>Amazon Review Sentiment Analysis</h4>
            </div>
            <div className="card-body">
              <p className="card-text">
                Based on {product.reviews.length} Amazon customer reviews, this product has a{' '}
                <span className={getSentimentClass(product.sentiment_score)}>
                  {product.sentiment_score >= 0.5 ? 'positive' : 
                   product.sentiment_score >= 0.3 ? 'neutral' : 'negative'} sentiment score
                </span>.
              </p>
              <div className="mb-4">
                <SentimentChart 
                  positive={product.sentiment_counts.positive}
                  neutral={product.sentiment_counts.neutral}
                  negative={product.sentiment_counts.negative}
                  product={product}
                />
              </div>
              
              <div className="row mb-3">
                <div className="col-md-4 text-center">
                  <div className="card h-100">
                    <div className="card-body">
                      <h5 className="sentiment-positive">
                        <i className="fas fa-thumbs-up mb-2 fa-2x"></i>
                        <div>{product.sentiment_counts.positive}</div>
                      </h5>
                      <div>Positive</div>
                    </div>
                  </div>
                </div>
                <div className="col-md-4 text-center">
                  <div className="card h-100">
                    <div className="card-body">
                      <h5 className="sentiment-neutral">
                        <i className="fas fa-balance-scale mb-2 fa-2x"></i>
                        <div>{product.sentiment_counts.neutral}</div>
                      </h5>
                      <div>Neutral</div>
                    </div>
                  </div>
                </div>
                <div className="col-md-4 text-center">
                  <div className="card h-100">
                    <div className="card-body">
                      <h5 className="sentiment-negative">
                        <i className="fas fa-thumbs-down mb-2 fa-2x"></i>
                        <div>{product.sentiment_counts.negative}</div>
                      </h5>
                      <div>Negative</div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Key Aspects Based on Amazon Review Analysis */}
              <div className="key-aspects mt-4">
                <h5>Key Aspects Mentioned in Reviews</h5>
                <div className="row">
                  <div className="col-md-6">
                    <div className="card border-success mb-3">
                      <div className="card-header bg-success text-white">
                        <i className="fas fa-plus-circle me-2"></i>Positive Aspects
                      </div>
                      <div className="card-body">
                        {product.key_aspects && product.key_aspects.positive && product.key_aspects.positive.length > 0 ? (
                          <div className="aspect-tags">
                            {Array.from(new Set(product.key_aspects.positive.map(k => k.keyword))).slice(0, 10).map((keyword, idx) => (
                              <span key={idx} className="badge bg-light text-success me-2 mb-2 p-2">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-muted">No significant positive aspects identified</p>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card border-danger mb-3">
                      <div className="card-header bg-danger text-white">
                        <i className="fas fa-minus-circle me-2"></i>Negative Aspects
                      </div>
                      <div className="card-body">
                        {product.key_aspects && product.key_aspects.negative && product.key_aspects.negative.length > 0 ? (
                          <div className="aspect-tags">
                            {Array.from(new Set(product.key_aspects.negative.map(k => k.keyword))).slice(0, 10).map((keyword, idx) => (
                              <span key={idx} className="badge bg-light text-danger me-2 mb-2 p-2">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-muted">No significant negative aspects identified</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Hype vs Reality Check */}
          {product.hype_vs_reality && <HypeVsRealityCheck hypeData={product.hype_vs_reality} />}

          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Customer Reviews</h4>
              <span className="badge bg-secondary">{product.reviews.length} Reviews</span>
            </div>
            <div className="card-body">
              <div className="review-list">
                {product.reviews.map((review, index) => (
                  <div key={index} className={`review-item ${getReviewClass(review.sentiment)}`}>
                    <div className="d-flex justify-content-between">
                      <h6>{review.author}</h6>
                      <div className={getSentimentClass(review.sentiment)}>
                        {getSentimentIcon(review.sentiment)} {review.sentiment.toFixed(2)}
                      </div>
                    </div>
                    <p>{review.text}</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <small className="text-muted">{review.date}</small>
                      {review.keywords && review.keywords.length > 0 && (
                        <div className="keywords-container">
                          <small className="text-muted me-2">Key aspects:</small>
                          {review.keywords.slice(0, 3).map((keyword, kidx) => (
                            <span key={kidx} className={`badge ${review.sentiment >= 0.5 ? 'bg-success' : review.sentiment >= 0.3 ? 'bg-warning' : 'bg-danger'} me-1`}>
                              {keyword.keyword}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;
