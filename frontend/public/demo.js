// DOM Elements
const productListEl = document.getElementById('product-list');
const productDetailEl = document.getElementById('product-detail');
const loginFormEl = document.getElementById('login-form');
const registerFormEl = document.getElementById('register-form');
const authFormsEl = document.getElementById('auth-forms');
const userInfoEl = document.getElementById('user-info');
const logoutBtnEl = document.getElementById('logout-btn');
const analyzeFormEl = document.getElementById('analyze-form');
const analysisResultEl = document.getElementById('analysis-result');

// State
let currentUser = null;
let products = [];
let selectedProduct = null;

// Fetch all products
async function fetchProducts() {
  try {
    const response = await fetch('/api/products');
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    products = await response.json();
    renderProductList();
  } catch (error) {
    console.error('Error fetching products:', error);
    showError('Failed to load products. Please try again later.');
  }
}

// Fetch product details
async function fetchProductDetails(productId) {
  try {
    const response = await fetch(`/api/products/${productId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch product details');
    }
    selectedProduct = await response.json();
    renderProductDetail();
  } catch (error) {
    console.error('Error fetching product details:', error);
    showError('Failed to load product details. Please try again later.');
  }
}

// Register user
async function registerUser(username, email, password) {
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Registration failed');
    }
    
    const data = await response.json();
    currentUser = data.user;
    updateAuthUI();
    
    // Show success message
    showSuccess('Registration successful! You are now logged in.');
  } catch (error) {
    console.error('Error registering user:', error);
    showError(error.message || 'Registration failed. Please try again.');
  }
}

// Login user
async function loginUser(username, password) {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Login failed');
    }
    
    const data = await response.json();
    currentUser = data.user;
    updateAuthUI();
    
    // Show success message
    showSuccess('Login successful!');
  } catch (error) {
    console.error('Error logging in:', error);
    showError(error.message || 'Login failed. Please try again.');
  }
}

// Logout user
async function logoutUser() {
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Logout failed');
    }
    
    currentUser = null;
    updateAuthUI();
    
    // Show success message
    showSuccess('You have been logged out successfully.');
  } catch (error) {
    console.error('Error logging out:', error);
    showError(error.message || 'Logout failed. Please try again.');
  }
}

// Analyze text sentiment
async function analyzeText(text) {
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Analysis failed');
    }
    
    const data = await response.json();
    renderAnalysisResult(data);
  } catch (error) {
    console.error('Error analyzing text:', error);
    showError(error.message || 'Analysis failed. Please try again.');
  }
}

// Check current user
async function checkCurrentUser() {
  try {
    const response = await fetch('/api/auth/user', {
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      currentUser = data.user;
    } else {
      currentUser = null;
    }
    
    updateAuthUI();
  } catch (error) {
    console.error('Error checking current user:', error);
    currentUser = null;
    updateAuthUI();
  }
}

// Render product list
function renderProductList() {
  if (!productListEl) return;
  
  productListEl.innerHTML = '';
  
  if (products.length === 0) {
    productListEl.innerHTML = '<div class="alert alert-info">No products found.</div>';
    return;
  }
  
  const row = document.createElement('div');
  row.className = 'row g-4';
  
  products.forEach(product => {
    // Calculate sentiment class
    let sentimentClass = 'bg-secondary';
    let sentimentText = 'Neutral';
    
    if (product.sentiment_score >= 0.6) {
      sentimentClass = 'bg-success';
      sentimentText = 'Positive';
    } else if (product.sentiment_score <= 0.4) {
      sentimentClass = 'bg-danger';
      sentimentText = 'Negative';
    }
    
    const col = document.createElement('div');
    col.className = 'col-md-4';
    col.innerHTML = `
      <div class="card h-100">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">${product.name}</h5>
          <span class="badge ${sentimentClass}">${sentimentText}</span>
        </div>
        <div class="card-body">
          <p class="card-text">${product.description}</p>
          <p class="card-text"><strong>Price:</strong> $${product.price.toFixed(2)}</p>
          <p class="card-text"><strong>Category:</strong> ${product.category}</p>
          <p class="card-text"><strong>Reviews:</strong> ${product.reviews ? product.reviews.length : 0}</p>
        </div>
        <div class="card-footer">
          <button class="btn btn-primary view-product" data-product-id="${product.id}">View Details</button>
        </div>
      </div>
    `;
    
    row.appendChild(col);
  });
  
  productListEl.appendChild(row);
  
  // Add event listeners to view product buttons
  document.querySelectorAll('.view-product').forEach(button => {
    button.addEventListener('click', function() {
      const productId = parseInt(this.getAttribute('data-product-id'));
      fetchProductDetails(productId);
    });
  });
}

// Render product detail
function renderProductDetail() {
  if (!productDetailEl || !selectedProduct) return;
  
  // Show product detail section and hide product list
  productListEl.style.display = 'none';
  productDetailEl.style.display = 'block';
  
  // Sentiment counts
  const sentimentCounts = selectedProduct.sentiment_counts || {
    positive: 0,
    neutral: 0,
    negative: 0
  };
  
  const totalReviews = sentimentCounts.positive + sentimentCounts.neutral + sentimentCounts.negative;
  
  // Calculate percentages
  const positivePercent = totalReviews > 0 ? Math.round((sentimentCounts.positive / totalReviews) * 100) : 0;
  const neutralPercent = totalReviews > 0 ? Math.round((sentimentCounts.neutral / totalReviews) * 100) : 0;
  const negativePercent = totalReviews > 0 ? Math.round((sentimentCounts.negative / totalReviews) * 100) : 0;
  
  // Format hype vs reality data
  let hypeRealityHTML = '<p>No hype vs reality analysis available.</p>';
  
  if (selectedProduct.hype_vs_reality) {
    const { matching_claims, contradicting_claims } = selectedProduct.hype_vs_reality;
    
    hypeRealityHTML = `
      <div class="mt-4">
        <h5>Claims Supported by Reviews:</h5>
        ${matching_claims.length > 0 
          ? `<ul>${matching_claims.map(claim => `<li>${claim}</li>`).join('')}</ul>` 
          : '<p>No supported claims found.</p>'}
        
        <h5 class="mt-3">Claims Contradicted by Reviews:</h5>
        ${contradicting_claims.length > 0 
          ? `<ul>${contradicting_claims.map(claim => `<li>${claim}</li>`).join('')}</ul>`
          : '<p>No contradicted claims found.</p>'}
      </div>
    `;
  }
  
  // Render key aspects
  let keyAspectsHTML = '<p>No key aspects available.</p>';
  
  if (selectedProduct.key_aspects) {
    const { positive, negative } = selectedProduct.key_aspects;
    
    keyAspectsHTML = `
      <div class="row">
        <div class="col-md-6">
          <h5 class="text-success">Positive Aspects:</h5>
          ${positive.length > 0 
            ? `<ul>${positive.slice(0, 5).map(aspect => `<li>${aspect}</li>`).join('')}</ul>`
            : '<p>No positive aspects found.</p>'}
        </div>
        <div class="col-md-6">
          <h5 class="text-danger">Negative Aspects:</h5>
          ${negative.length > 0 
            ? `<ul>${negative.slice(0, 5).map(aspect => `<li>${aspect}</li>`).join('')}</ul>`
            : '<p>No negative aspects found.</p>'}
        </div>
      </div>
    `;
  }
  
  // Render reviews with sentiment
  let reviewsHTML = '<p>No reviews available.</p>';
  
  if (selectedProduct.reviews && selectedProduct.reviews.length > 0) {
    reviewsHTML = `
      <div class="mt-4">
        <h5>Customer Reviews:</h5>
        <div class="list-group">
          ${selectedProduct.reviews.map(review => {
            let sentimentClass = 'bg-secondary';
            let sentimentText = 'Neutral';
            
            if (review.sentiment >= 0.6) {
              sentimentClass = 'bg-success';
              sentimentText = 'Positive';
            } else if (review.sentiment <= 0.4) {
              sentimentClass = 'bg-danger';
              sentimentText = 'Negative';
            }
            
            return `
              <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <h6>${review.author || 'Anonymous'}</h6>
                  <span class="badge ${sentimentClass}">${sentimentText}</span>
                </div>
                <p>${review.text}</p>
                ${review.date ? `<small class="text-muted">Date: ${review.date}</small>` : ''}
                ${review.keywords && review.keywords.length > 0 ? 
                  `<div class="mt-2">
                    <small class="text-muted">Key points: ${review.keywords.join(', ')}</small>
                  </div>` : ''}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }
  
  productDetailEl.innerHTML = `
    <div class="mb-4">
      <button id="back-to-products" class="btn btn-secondary mb-4">
        <i class="fas fa-arrow-left"></i> Back to Products
      </button>
      
      <div class="card">
        <div class="card-header">
          <h3>${selectedProduct.name}</h3>
        </div>
        <div class="card-body">
          <p class="lead">${selectedProduct.description}</p>
          
          <div class="row mb-4">
            <div class="col-md-6">
              <p><strong>Price:</strong> $${selectedProduct.price.toFixed(2)}</p>
              <p><strong>Category:</strong> ${selectedProduct.category}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Overall Sentiment:</strong></p>
              <div class="progress mb-3" style="height: 25px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${positivePercent}%" 
                  aria-valuenow="${positivePercent}" aria-valuemin="0" aria-valuemax="100">
                  Positive ${positivePercent}%
                </div>
                <div class="progress-bar bg-secondary" role="progressbar" style="width: ${neutralPercent}%" 
                  aria-valuenow="${neutralPercent}" aria-valuemin="0" aria-valuemax="100">
                  Neutral ${neutralPercent}%
                </div>
                <div class="progress-bar bg-danger" role="progressbar" style="width: ${negativePercent}%" 
                  aria-valuenow="${negativePercent}" aria-valuemin="0" aria-valuemax="100">
                  Negative ${negativePercent}%
                </div>
              </div>
              <p><small class="text-muted">Based on ${totalReviews} reviews</small></p>
            </div>
          </div>
          
          <div class="card mb-4">
            <div class="card-header bg-info text-white">
              <h4>Key Aspects</h4>
            </div>
            <div class="card-body">
              ${keyAspectsHTML}
            </div>
          </div>
          
          <div class="card mb-4">
            <div class="card-header bg-primary text-white">
              <h4>Hype vs. Reality Check</h4>
            </div>
            <div class="card-body">
              ${hypeRealityHTML}
            </div>
          </div>
          
          ${reviewsHTML}
        </div>
      </div>
    </div>
  `;
  
  // Add event listener to back button
  document.getElementById('back-to-products').addEventListener('click', function() {
    productDetailEl.style.display = 'none';
    productListEl.style.display = 'block';
  });
}

// Render analysis result
function renderAnalysisResult(data) {
  if (!analysisResultEl) return;
  
  let sentimentClass = 'bg-secondary';
  let sentimentText = 'Neutral';
  
  if (data.sentiment_score >= 0.6) {
    sentimentClass = 'bg-success';
    sentimentText = 'Positive';
  } else if (data.sentiment_score <= 0.4) {
    sentimentClass = 'bg-danger';
    sentimentText = 'Negative';
  }
  
  analysisResultEl.innerHTML = `
    <div class="card mt-3">
      <div class="card-header ${sentimentClass.replace('bg-', 'bg-')} text-white">
        <h5 class="mb-0">Sentiment Analysis Result: ${sentimentText}</h5>
      </div>
      <div class="card-body">
        <p><strong>Text:</strong> ${data.text}</p>
        <p><strong>Sentiment Score:</strong> ${data.sentiment_score.toFixed(2)}</p>
        <div class="progress">
          <div class="progress-bar ${sentimentClass}" role="progressbar" 
            style="width: ${data.sentiment_score * 100}%" 
            aria-valuenow="${data.sentiment_score * 100}" 
            aria-valuemin="0" aria-valuemax="100">
            ${(data.sentiment_score * 100).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  `;
}

// Update authentication UI based on current user
function updateAuthUI() {
  if (currentUser) {
    // User is logged in
    if (authFormsEl) authFormsEl.style.display = 'none';
    if (userInfoEl) {
      userInfoEl.style.display = 'block';
      userInfoEl.innerHTML = `
        <div class="card">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Welcome, ${currentUser.username}!</h5>
          </div>
          <div class="card-body">
            <p><strong>Email:</strong> ${currentUser.email}</p>
            <button id="logout-btn" class="btn btn-danger">Logout</button>
          </div>
        </div>
      `;
      
      // Add event listener to logout button
      document.getElementById('logout-btn').addEventListener('click', logoutUser);
    }
  } else {
    // User is not logged in
    if (authFormsEl) authFormsEl.style.display = 'block';
    if (userInfoEl) userInfoEl.style.display = 'none';
  }
}

// Show error message
function showError(message) {
  const alertEl = document.createElement('div');
  alertEl.className = 'alert alert-danger alert-dismissible fade show';
  alertEl.role = 'alert';
  alertEl.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  document.querySelector('.alerts-container').appendChild(alertEl);
  
  // Auto dismiss after 5 seconds
  setTimeout(() => {
    alertEl.classList.remove('show');
    setTimeout(() => alertEl.remove(), 150);
  }, 5000);
}

// Show success message
function showSuccess(message) {
  const alertEl = document.createElement('div');
  alertEl.className = 'alert alert-success alert-dismissible fade show';
  alertEl.role = 'alert';
  alertEl.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  document.querySelector('.alerts-container').appendChild(alertEl);
  
  // Auto dismiss after 5 seconds
  setTimeout(() => {
    alertEl.classList.remove('show');
    setTimeout(() => alertEl.remove(), 150);
  }, 5000);
}

// Event listeners for forms
document.addEventListener('DOMContentLoaded', function() {
  // Check current user
  checkCurrentUser();
  
  // Fetch products
  fetchProducts();
  
  // Register form
  if (registerFormEl) {
    registerFormEl.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const username = document.getElementById('register-username').value;
      const email = document.getElementById('register-email').value;
      const password = document.getElementById('register-password').value;
      
      registerUser(username, email, password);
    });
  }
  
  // Login form
  if (loginFormEl) {
    loginFormEl.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;
      
      loginUser(username, password);
    });
  }
  
  // Analyze form
  if (analyzeFormEl) {
    analyzeFormEl.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const text = document.getElementById('analyze-text').value;
      
      if (text.trim() === '') {
        showError('Please enter some text to analyze.');
        return;
      }
      
      analyzeText(text);
    });
  }
  
  // Switch between login and register forms
  document.getElementById('switch-to-register')?.addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'block';
  });
  
  document.getElementById('switch-to-login')?.addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('register-container').style.display = 'none';
    document.getElementById('login-container').style.display = 'block';
  });
});