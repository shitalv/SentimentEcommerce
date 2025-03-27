import React from 'react';

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <a className="navbar-brand" href="/">
          <i className="fas fa-chart-line me-2"></i>
          SentimentShop
        </a>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav" 
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <a className="nav-link active" href="/">Products</a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="/">Insights</a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="/">About</a>
            </li>
          </ul>
          <div className="d-flex">
            <button className="btn btn-outline-light me-2" type="button">
              <i className="fas fa-shopping-cart me-1"></i> Cart (0)
            </button>
            <button className="btn btn-outline-secondary" type="button">
              <i className="fas fa-user me-1"></i> Login
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
