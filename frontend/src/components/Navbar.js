import React from 'react';

function Navbar({ currentUser, onLogout, onLoginClick }) {
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
            
            {currentUser ? (
              <div className="dropdown">
                <button 
                  className="btn btn-outline-success dropdown-toggle" 
                  type="button" 
                  id="userDropdown" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  <i className="fas fa-user-circle me-1"></i>
                  {currentUser.username}
                </button>
                <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                  <li>
                    <button className="dropdown-item" type="button">
                      <i className="fas fa-cog me-2"></i>Profile
                    </button>
                  </li>
                  <li>
                    <button className="dropdown-item" type="button">
                      <i className="fas fa-history me-2"></i>Order History
                    </button>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <button 
                      className="dropdown-item text-danger" 
                      type="button"
                      onClick={onLogout}
                    >
                      <i className="fas fa-sign-out-alt me-2"></i>Logout
                    </button>
                  </li>
                </ul>
              </div>
            ) : (
              <button 
                className="btn btn-outline-secondary" 
                type="button"
                onClick={onLoginClick}
              >
                <i className="fas fa-sign-in-alt me-1"></i> Login
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
