import React from 'react';

function SearchFilter({ 
  searchTerm, 
  setSearchTerm, 
  sentimentFilter, 
  setSentimentFilter,
  categoryFilter,
  setCategoryFilter,
  categories
}) {
  return (
    <div className="card mb-4">
      <div className="card-body">
        <h5 className="card-title mb-3">Search & Filter</h5>
        <div className="row g-3">
          <div className="col-md-6">
            <div className="input-group">
              <span className="input-group-text">
                <i className="fas fa-search"></i>
              </span>
              <input
                type="text"
                className="form-control"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button 
                  className="btn btn-outline-secondary" 
                  type="button"
                  onClick={() => setSearchTerm('')}
                >
                  <i className="fas fa-times"></i>
                </button>
              )}
            </div>
          </div>
          <div className="col-md-3">
            <select 
              className="form-select"
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive Reviews</option>
              <option value="neutral">Neutral Reviews</option>
              <option value="negative">Negative Reviews</option>
            </select>
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SearchFilter;
