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
let productRecommendations = [];

// Fetch all products
async function fetchProducts() {
  try {
    console.log("Fetching products...");
    const response = await fetch('/api/products');
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    const data = await response.json();
    
    // Ensure we have the correct data structure
    console.log("Raw product data received:", data);
    
    // Handle both formats: If products is a property or if the response directly contains the array
    products = data.products || data || [];
    
    // Add detailed logging for debugging undefined values
    if (products.length > 0) {
      console.log("First product sample:", JSON.stringify(products[0]));
    }
    
    // Update the product data structure to include sentiment score property
    // and ensure no undefined values appear in the UI
    products = products.map(product => {
      // Ensure product has all required fields with defaults if missing
      const enhancedProduct = {
        // Basic properties with defaults
        id: product.id || "unknown",
        name: product.name || "Unknown Product",
        description: product.description || "No description available",
        price: product.price || 0,
        category: product.category || "Uncategorized",
        image_url: product.image_url || "/placeholder.jpg",
        reviews: product.reviews || [],
        
        // Ensure sentiment data is always present
        sentiment: product.sentiment || { positive: 0.5, neutral: 0.3, negative: 0.2 },
        // Make sure review_count is always included
        review_count: product.review_count || 0
      };
      
      // Add sentiment_score for compatibility with filtering
      enhancedProduct.sentiment_score = enhancedProduct.sentiment.positive;
      
      return enhancedProduct;
    });
    
    console.log("Enhanced products:", products);
    renderProductList();
  } catch (error) {
    console.error('Error fetching products:', error);
    showError('Failed to load products. Please try again later.');
  }
}

// Fetch product details
async function fetchProductDetails(productId) {
  try {
    // Extract full ID from productId if it's a partial ID
    // The frontend might be receiving just the first few characters
    console.log(`Fetching details for product ID (Original): ${productId}`);
    
    // Find the full product ID from our products list if we have a partial ID
    let fullProductId = productId;
    
    // Try to find the product with full ID in our existing products array
    if (products && products.length > 0) {
      const matchingProduct = products.find(p => p.id === productId);
      
      if (!matchingProduct && productId.length < 24) {
        // Look for a product whose ID starts with the partial ID
        const matchByPartial = products.find(p => p.id.startsWith(productId));
        if (matchByPartial) {
          fullProductId = matchByPartial.id;
          console.log(`Found matching product with full ID: ${fullProductId}`);
        }
      }
    }
    
    console.log(`Using full product ID for fetch: ${fullProductId}`);
    const response = await fetch(`/api/products/${fullProductId}`)
      .catch(err => {
        console.log("Network error fetching product details:", err);
        throw new Error("Network error when fetching product details");
      });

    if (!response.ok) {
      console.error(`Failed to fetch product details: ${response.status}`);
      throw new Error(`Failed to fetch product details: ${response.status}`);
    }

    const data = await response.json();
    console.log("Raw product detail data:", data);
    
    selectedProduct = data.product || {};
    
    // In case the response doesn't have product wrapped, try the direct data
    if (Object.keys(selectedProduct).length === 0 && data) {
      // Check if data itself is the product
      if (data.id || data.name) {
        selectedProduct = data;
      }
    }
    
    console.log("Selected product after unwrapping:", selectedProduct);
    
    // Add defaults for any missing fields to prevent undefined in UI
    selectedProduct = {
      id: selectedProduct.id || fullProductId,
      name: selectedProduct.name || "Unknown Product",
      description: selectedProduct.description || "No description available",
      price: selectedProduct.price || 0,
      category: selectedProduct.category || "Uncategorized",
      image_url: selectedProduct.image_url || "/placeholder.jpg",
      reviews: selectedProduct.reviews || [],
      review_count: selectedProduct.review_count || (selectedProduct.reviews ? selectedProduct.reviews.length : 0),
      sentiment: selectedProduct.sentiment || { positive: 0, neutral: 0, negative: 0 }
    };
    
    // Extract key aspects from reviews if not already provided
    if (!selectedProduct.key_aspects) {
      console.log("Generating key aspects from reviews");
      selectedProduct.key_aspects = extractKeyAspectsFromReviews(selectedProduct.reviews || []);
    }
    
    // Generate Hype vs. Reality analysis if not already provided
    if (!selectedProduct.hype_vs_reality) {
      console.log("Generating Hype vs. Reality analysis");
      selectedProduct.hype_vs_reality = analyzeHypeVsReality(selectedProduct.description, selectedProduct.reviews || []);
    }
    
    console.log("IMPORTANT - Raw sentiment data:", selectedProduct.sentiment);
    console.log("Key aspects:", selectedProduct.key_aspects);
    console.log("Hype vs. Reality:", selectedProduct.hype_vs_reality);
    
    // If we have a review count but all sentiment scores are 0, adjust sentiment to reflect reviews
    if (selectedProduct.review_count > 0 && 
        selectedProduct.sentiment.positive === 0 && 
        selectedProduct.sentiment.neutral === 0 && 
        selectedProduct.sentiment.negative === 0) {
        
        // Default distribution when we have reviews but no sentiment data
        selectedProduct.sentiment = {
            positive: 0.7,  // 70% positive by default
            neutral: 0.2,   // 20% neutral
            negative: 0.1   // 10% negative
        };
        console.log("Applied default sentiment distribution for product with reviews");
    }
    
    // Add sentiment_score property for compatibility with existing code
    selectedProduct.sentiment_score = selectedProduct.sentiment.positive;
    
    // Create sentiment_counts for the product detail view
    // For percentage calculations, we interpret the sentiment values differently based on what they represent
    let totalSentiment = selectedProduct.sentiment.positive + selectedProduct.sentiment.neutral + selectedProduct.sentiment.negative;
    
    // If the total is 0 or very small, these are likely ratios already
    if (totalSentiment < 0.01) {
        // Default to neutral distribution
        selectedProduct.sentiment_counts = {
          positive: 0,
          neutral: 100,
          negative: 0
        };
    } 
    // If sentiment values are between 0-1, they're likely ratios already
    else if (totalSentiment <= 3) {
        selectedProduct.sentiment_counts = {
          positive: Math.round(selectedProduct.sentiment.positive * 100),
          neutral: Math.round(selectedProduct.sentiment.neutral * 100),
          negative: Math.round(selectedProduct.sentiment.negative * 100)
        };
    } 
    // Otherwise, they're likely raw counts
    else {
        selectedProduct.sentiment_counts = {
          positive: Math.round((selectedProduct.sentiment.positive / totalSentiment) * 100),
          neutral: Math.round((selectedProduct.sentiment.neutral / totalSentiment) * 100),
          negative: Math.round((selectedProduct.sentiment.negative / totalSentiment) * 100)
        };
    }
    
    console.log("Calculated sentiment counts:", selectedProduct.sentiment_counts);
    
    console.log("Final product details with defaults:", selectedProduct);
    
    // Also fetch recommendations for this product
    fetchProductRecommendations(fullProductId);
    
    renderProductDetail();
  } catch (error) {
    console.error('Error fetching product details:', error);
    showError('Failed to load product details. Please try again later.');
  }
}

// Fetch product recommendations
async function fetchProductRecommendations(productId) {
  try {
    console.log(`Fetching recommendations for product ID: ${productId}`);
    const response = await fetch(`/api/products/${productId}/recommendations?limit=4`)
      .catch(err => {
        console.log("Network error fetching recommendations:", err);
        throw new Error("Network error when fetching recommendations");
      });

    if (!response.ok) {
      console.error(`Failed to fetch recommendations: ${response.status}`);
      throw new Error(`Failed to fetch recommendations: ${response.status}`);
    }

    const data = await response.json();
    productRecommendations = data.recommendations || [];
    
    // Add sentiment_score for compatibility with existing code
    productRecommendations = productRecommendations.map(product => {
      if (product.sentiment) {
        product.sentiment_score = product.sentiment.positive;
      } else {
        product.sentiment_score = 0.5; // Default neutral
      }
      return product;
    });
    
    console.log("Recommendations fetched:", productRecommendations);
    
    // Update recommendations section if it exists
    renderProductRecommendations();
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    productRecommendations = [];
    renderProductRecommendations();
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
    console.log("Checking current user...");
    const response = await fetch('/api/auth/user', {
      credentials: 'include'
    })
    .catch(err => {
      console.log("Network error checking user:", err);
      return { ok: false };
    });

    if (response.ok) {
      const data = await response.json();
      currentUser = data.user;
      console.log("User logged in:", currentUser);
    } else {
      console.log("No user logged in");
      currentUser = null;
    }

    updateAuthUI();
  } catch (error) {
    console.error('Error checking current user:', error);
    currentUser = null;
    updateAuthUI();
  }
}

// Analyze product description vs review sentiment
function analyzeHypeVsReality(description, reviews) {
  // Default return structure
  const result = {
    matching_claims: [],
    contradicting_claims: []
  };
  
  // Exit early if there's no description or no reviews
  if (!description || !reviews || reviews.length === 0) {
    return result;
  }
  
  // Normalize description to lowercase
  const desc = description ? description.toLowerCase() : "";
  if (desc === "") {
    return result;
  }
  
  // Set of marketing claim phrases to look for
  const marketingClaims = [
    { term: "best", context: null },
    { term: "perfect", context: null },
    { term: "excellent", context: null },
    { term: "amazing", context: null },
    { term: "outstanding", context: null },
    { term: "revolutionary", context: null },
    { term: "innovative", context: null },
    { term: "premium", context: null },
    { term: "high-quality", context: null },
    { term: "top-rated", context: null },
    { term: "professional", context: null },
    { term: "durable", context: null },
    { term: "long-lasting", context: null },
    { term: "easy to use", context: null },
    { term: "efficient", context: null },
    { term: "fastest", context: null },
    { term: "finest", context: null },
    { term: "superior", context: null },
    { term: "advanced", context: null },
    { term: "state-of-the-art", context: null },
    { term: "cutting-edge", context: null },
    { term: "reliable", context: null },
    { term: "exceptional", context: null }
  ];
  
  // Extract context for each claim from the description
  marketingClaims.forEach(claim => {
    if (desc.includes(claim.term)) {
      // Get surrounding context
      const words = desc.split(/\s+/);
      for (let i = 0; i < words.length; i++) {
        if (words[i].includes(claim.term) || (i < words.length - 1 && `${words[i]} ${words[i+1]}`.includes(claim.term))) {
          const start = Math.max(0, i - 4);
          const end = Math.min(words.length, i + 5);
          claim.context = words.slice(start, end).join(" ");
          break;
        }
      }
    }
  });
  
  // Only keep claims that were found in the description
  const foundClaims = marketingClaims.filter(claim => claim.context !== null);
  
  // Analyze each review to see if it supports or contradicts the claims
  foundClaims.forEach(claim => {
    let supporting = 0;
    let contradicting = 0;
    
    reviews.forEach(review => {
      const reviewText = review.text ? review.text.toLowerCase() : "";
      
      // Skip empty reviews
      if (!reviewText) return;
      
      // Get review sentiment
      let sentiment;
      if (review.sentiment && typeof review.sentiment === 'object' && review.sentiment.score !== undefined) {
        sentiment = review.sentiment.score;
      } else if (review.sentiment && typeof review.sentiment === 'number') {
        sentiment = review.sentiment;
      } else if (review.rating && typeof review.rating === 'number') {
        sentiment = Math.min(1, Math.max(0, review.rating / 5));
      } else {
        sentiment = 0.5;  // Default neutral
      }
      
      const isPositive = sentiment >= 0.6;
      const isNegative = sentiment <= 0.4;
      
      // Check if the review mentions the claim term
      if (reviewText.includes(claim.term)) {
        // If review directly mentions the claim term, categorize by sentiment
        if (isPositive) {
          supporting++;
        } else if (isNegative) {
          contradicting++;
        }
      }
      
      // Check for negations of claim term
      const negationPatterns = [
        `not ${claim.term}`, 
        `isn't ${claim.term}`, 
        `isnt ${claim.term}`,
        `doesn't ${claim.term}`, 
        `doesnt ${claim.term}`, 
        `far from ${claim.term}`,
        `barely ${claim.term}`, 
        `hardly ${claim.term}`
      ];
      
      for (const pattern of negationPatterns) {
        if (reviewText.includes(pattern)) {
          contradicting++;
          break;
        }
      }
    });
    
    // Categorize claim as matched or contradicted based on review evidence
    const claimText = `"${claim.term}" (in context: "${claim.context}")`;
    
    if (supporting > contradicting && supporting > 0) {
      result.matching_claims.push(claimText);
    } else if (contradicting > 0) {
      result.contradicting_claims.push(claimText);
    } else if (supporting === 0 && contradicting === 0) {
      // If there's no evidence either way, don't include the claim
    }
  });
  
  return result;
}

// Extract key aspects from reviews
function extractKeyAspectsFromReviews(reviews) {
  // Exit early if there are no reviews
  if (!reviews || reviews.length === 0) {
    return { positive: [], negative: [] };
  }
  
  console.log("Extracting key aspects from", reviews.length, "reviews");
  
  // Categories of aspects we want to extract
  const aspectCategories = {
    quality: ["quality", "build", "material", "construction", "durability", "sturdy", "solid"],
    performance: ["performance", "speed", "fast", "slow", "response", "responsive", "lag"],
    features: ["feature", "functionality", "function", "capability"],
    usability: ["easy", "intuitive", "simple", "user-friendly", "difficult", "complicated", "confusing"],
    value: ["price", "value", "worth", "expensive", "cheap", "cost", "affordable", "overpriced"],
    design: ["design", "look", "appearance", "style", "aesthetic", "color", "size", "weight"],
    reliability: ["reliable", "consistent", "dependable", "unreliable", "issue", "problem", "fail"]
  };
  
  // Initialize arrays to store positive and negative aspects
  const positiveAspects = new Map();
  const negativeAspects = new Map();
  
  // Process each review
  reviews.forEach(review => {
    // Get review text and sentiment
    const text = review.text ? review.text.toLowerCase() : "";
    
    // Skip empty reviews
    if (!text) return;
    
    // Determine if the review is positive or negative
    let sentiment;
    if (review.sentiment && typeof review.sentiment === 'object' && review.sentiment.score !== undefined) {
      sentiment = review.sentiment.score;
    } else if (review.sentiment && typeof review.sentiment === 'number') {
      sentiment = review.sentiment;
    } else if (review.rating && typeof review.rating === 'number') {
      // Convert 5-star rating to sentiment score (0-1)
      sentiment = Math.min(1, Math.max(0, review.rating / 5));
    } else {
      // Default to neutral
      sentiment = 0.5;
    }
    
    const isPositive = sentiment >= 0.5;
    
    // Look for aspect keywords in the review
    Object.entries(aspectCategories).forEach(([category, keywords]) => {
      keywords.forEach(keyword => {
        if (text.includes(keyword)) {
          // Find the surrounding context (3 words before and after)
          const words = text.split(/\s+/);
          let context = "";
          
          for (let i = 0; i < words.length; i++) {
            if (words[i].includes(keyword)) {
              // Get context (3 words before and after the keyword)
              const start = Math.max(0, i - 3);
              const end = Math.min(words.length, i + 4);
              context = words.slice(start, end).join(" ");
              break;
            }
          }
          
          // Create aspect entry with category and context
          const aspect = {
            keyword: keyword,
            category: category,
            context: context || `${keyword} mentioned`,
            count: 1
          };
          
          // Add to appropriate map based on sentiment
          if (isPositive) {
            if (positiveAspects.has(keyword)) {
              const existing = positiveAspects.get(keyword);
              existing.count += 1;
              positiveAspects.set(keyword, existing);
            } else {
              positiveAspects.set(keyword, aspect);
            }
          } else {
            if (negativeAspects.has(keyword)) {
              const existing = negativeAspects.get(keyword);
              existing.count += 1;
              negativeAspects.set(keyword, existing);
            } else {
              negativeAspects.set(keyword, aspect);
            }
          }
        }
      });
    });
  });
  
  // Convert maps to arrays and sort by count
  const positiveArray = Array.from(positiveAspects.values())
    .sort((a, b) => b.count - a.count)
    .map(aspect => `${aspect.keyword} (${aspect.context})`);
    
  const negativeArray = Array.from(negativeAspects.values())
    .sort((a, b) => b.count - a.count)
    .map(aspect => `${aspect.keyword} (${aspect.context})`);
  
  return {
    positive: positiveArray,
    negative: negativeArray
  };
}

// Filter products based on search and filter criteria
function filterProducts() {
  const searchText = document.getElementById('product-search')?.value.toLowerCase() || '';
  const categoryFilter = document.getElementById('category-filter')?.value || '';
  const sentimentFilter = document.getElementById('sentiment-filter')?.value || '';

  return products.filter(product => {
    // Search by name or description
    const matchesSearch = searchText === '' || 
      product.name.toLowerCase().includes(searchText) || 
      product.description.toLowerCase().includes(searchText);

    // Filter by category
    const matchesCategory = categoryFilter === '' || product.category === categoryFilter;

    // Filter by sentiment
    let matchesSentiment = true;
    if (sentimentFilter !== '') {
      if (sentimentFilter === 'positive' && product.sentiment_score < 0.6) {
        matchesSentiment = false;
      } else if (sentimentFilter === 'neutral' && (product.sentiment_score < 0.4 || product.sentiment_score > 0.6)) {
        matchesSentiment = false;
      } else if (sentimentFilter === 'negative' && product.sentiment_score > 0.4) {
        matchesSentiment = false;
      }
    }

    return matchesSearch && matchesCategory && matchesSentiment;
  });
}

// Render product list
function renderProductList() {
  if (!productListEl) return;

  productListEl.innerHTML = '';

  // Apply filters
  const filteredProducts = filterProducts();

  if (filteredProducts.length === 0) {
    productListEl.innerHTML = '<div class="alert alert-info">No products found matching your criteria.</div>';
    return;
  }

  const row = document.createElement('div');
  row.className = 'row g-4';

  filteredProducts.forEach(product => {
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
          <p class="card-text"><strong>Price:</strong> $${product.price ? product.price.toFixed(2) : 'N/A'}</p>
          <p class="card-text"><strong>Category:</strong> ${product.category}</p>
          <p class="card-text"><strong>Reviews:</strong> ${product.review_count || (product.reviews ? product.reviews.length : 0)}</p>
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
      // Get product ID as string (MongoDB ObjectIDs are strings)
      const productId = this.getAttribute('data-product-id');
      console.log(`View product button clicked for ID: ${productId}`);
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
  // Use sentiment data for visualization
  const sentimentCounts = selectedProduct.sentiment_counts || {
    positive: Math.round(selectedProduct.sentiment.positive * 100),
    neutral: Math.round(selectedProduct.sentiment.neutral * 100),
    negative: Math.round(selectedProduct.sentiment.negative * 100)
  };

  // For total count, prioritize the backend review_count field
  const totalReviews = selectedProduct.review_count || 
                      (selectedProduct.reviews ? selectedProduct.reviews.length : 
                      (sentimentCounts.positive + sentimentCounts.neutral + sentimentCounts.negative));

  // Use the sentiment_counts which are already calculated as percentages
  let positivePercent = selectedProduct.sentiment_counts.positive;
  let neutralPercent = selectedProduct.sentiment_counts.neutral;
  let negativePercent = selectedProduct.sentiment_counts.negative;
  
  // For safety, ensure they add up to 100% (sometimes there can be rounding errors)
  const total = positivePercent + neutralPercent + negativePercent;
  if (total > 0 && total !== 100) {
    // Normalize to ensure they add up to 100%
    positivePercent = Math.round((positivePercent / total) * 100);
    neutralPercent = Math.round((neutralPercent / total) * 100);
    negativePercent = 100 - positivePercent - neutralPercent;
  }
  
  // If we have review count but no sentiment distribution, default to balanced distribution
  if (totalReviews > 0 && total === 0) {
    console.log("No sentiment distribution for product with reviews, using defaults");
    positivePercent = 70;  // Default to 70% positive
    neutralPercent = 20;   // 20% neutral
    negativePercent = 10;  // 10% negative
  }
  
  console.log(`Final percentages for display: Positive=${positivePercent}%, Neutral=${neutralPercent}%, Negative=${negativePercent}%`);

  // Format hype vs reality data
  let hypeRealityHTML = '<p>No marketing claims found in product description to analyze.</p>';

  if (selectedProduct.hype_vs_reality) {
    const { matching_claims, contradicting_claims } = selectedProduct.hype_vs_reality;
    
    // If we have any claims to display
    if (matching_claims.length > 0 || contradicting_claims.length > 0) {
      hypeRealityHTML = `
        <div class="mt-4">
          <div class="row">
            <div class="col-md-6">
              <div class="card bg-success-subtle mb-3">
                <div class="card-header bg-success text-white">
                  <h5 class="mb-0"><i class="fas fa-check-circle me-2"></i>Claims Supported by Reviews</h5>
                </div>
                <div class="card-body">
                  ${matching_claims.length > 0 
                    ? `<ul class="list-group list-group-flush">
                        ${matching_claims.map(claim => `
                          <li class="list-group-item bg-success-subtle">
                            <i class="fas fa-thumbs-up text-success me-2"></i>${claim}
                          </li>`).join('')}
                      </ul>` 
                    : '<p class="card-text">No marketing claims were supported by customer reviews.</p>'}
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card bg-danger-subtle mb-3">
                <div class="card-header bg-danger text-white">
                  <h5 class="mb-0"><i class="fas fa-exclamation-circle me-2"></i>Claims Contradicted by Reviews</h5>
                </div>
                <div class="card-body">
                  ${contradicting_claims.length > 0 
                    ? `<ul class="list-group list-group-flush">
                        ${contradicting_claims.map(claim => `
                          <li class="list-group-item bg-danger-subtle">
                            <i class="fas fa-thumbs-down text-danger me-2"></i>${claim}
                          </li>`).join('')}
                      </ul>`
                    : '<p class="card-text">No marketing claims were contradicted by customer reviews.</p>'}
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }
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
            
            // Handle both direct sentiment score and nested sentiment object
            const sentimentScore = review.sentiment && review.sentiment.score !== undefined 
                                 ? review.sentiment.score 
                                 : (typeof review.sentiment === 'number' ? review.sentiment : 0.5);
                                 
            if (sentimentScore >= 0.6) {
              sentimentClass = 'bg-success';
              sentimentText = 'Positive';
            } else if (sentimentScore <= 0.4) {
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
                ${(() => {
                  // Handle both direct keywords array and nested keywords in sentiment
                  const keywords = review.keywords || 
                                  (review.sentiment && review.sentiment.keywords ? 
                                   review.sentiment.keywords : null);
                                   
                  if (keywords && Array.isArray(keywords) && keywords.length > 0) {
                    return `<div class="mt-2">
                      <small class="text-muted">Key points: ${keywords.join(', ')}</small>
                    </div>`;
                  }
                  return '';
                })()}
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
              <p><strong>Price:</strong> $${selectedProduct.price ? selectedProduct.price.toFixed(2) : 'N/A'}</p>
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
              <p><small class="text-muted">Based on ${selectedProduct.review_count || totalReviews} reviews</small></p>
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
    // Reset recommendations when going back to product list
    productRecommendations = [];
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

// Render product recommendations
function renderProductRecommendations() {
  const recommendationsContainer = document.getElementById('product-recommendations');
  if (!recommendationsContainer) {
    // Create recommendations container if it doesn't exist
    const container = document.createElement('div');
    container.id = 'product-recommendations';
    container.className = 'card mb-4';
    
    if (productDetailEl) {
      // Find a good place to insert the recommendations
      const cards = productDetailEl.querySelectorAll('.card');
      if (cards.length > 0) {
        // Insert after the first card
        cards[0].parentNode.insertBefore(container, cards[0].nextSibling);
      } else {
        // Append to the product detail element
        productDetailEl.appendChild(container);
      }
    }
    
    renderProductRecommendations();
    return;
  }
  
  // Render recommendations
  if (productRecommendations.length === 0) {
    recommendationsContainer.innerHTML = `
      <div class="card-header bg-light">
        <h4>Similar Products You Might Like</h4>
      </div>
      <div class="card-body text-center py-4">
        <p class="text-muted">No recommendations available for this product.</p>
      </div>
    `;
    return;
  }
  
  // Render recommendation list
  let recommendationsHTML = `
    <div class="card-header bg-success text-white">
      <h4><i class="fas fa-thumbs-up me-2"></i>Recommended Products Based on Sentiment Analysis</h4>
    </div>
    <div class="card-body">
      <p class="text-muted mb-3">
        These product recommendations are generated based on sentiment analysis of reviews and product characteristics.
      </p>
      <div class="row">
  `;
  
  // Add each recommendation
  productRecommendations.forEach(product => {
    // Determine sentiment color
    let sentimentColor = 'secondary';
    
    if (product.sentiment_scores) {
      const { positive, neutral, negative } = product.sentiment_scores;
      if (positive > neutral && positive > negative) {
        sentimentColor = 'success';
      } else if (negative > positive && negative > neutral) {
        sentimentColor = 'danger';
      } else {
        sentimentColor = 'warning';
      }
    }
    
    recommendationsHTML += `
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 shadow-sm">
          <div class="card-header text-center bg-light">
            <span class="badge bg-${sentimentColor} position-absolute top-0 end-0 mt-2 me-2">
              <i class="fas fa-star me-1"></i>
              ${product.sentiment_scores?.positive ? (product.sentiment_scores.positive * 10).toFixed(1) : 'N/A'}
            </span>
            <div class="text-center py-3 bg-light">
              <svg class="bd-placeholder-img" width="100" height="100" xmlns="http://www.w3.org/2000/svg" 
                role="img" preserveAspectRatio="xMidYMid slice" focusable="false">
                <title>${product.name}</title>
                <rect width="100%" height="100%" fill="#55595c"/>
                <text x="50%" y="50%" fill="#eceeef" dy=".3em">${product.name.substring(0, 5)}</text>
              </svg>
            </div>
          </div>
          <div class="card-body">
            <h6 class="card-title">${product.name}</h6>
            <div class="d-flex justify-content-between align-items-center mt-2">
              <span class="badge bg-secondary">${product.category || 'Unknown'}</span>
              <span class="price">$${product.price ? product.price.toFixed(2) : 'N/A'}</span>
            </div>
          </div>
          <div class="card-footer bg-white border-top-0">
            <button class="btn btn-outline-primary btn-sm w-100" 
              onclick="fetchProductDetails(${product.id})">
              View Details
            </button>
          </div>
        </div>
      </div>
    `;
  });
  
  recommendationsHTML += `
      </div>
    </div>
  `;
  
  recommendationsContainer.innerHTML = recommendationsHTML;
}

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

  // Search input - search as you type
  const searchInput = document.getElementById('product-search');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      renderProductList();
    });
  }

  // Apply filters button
  const applyFiltersBtn = document.getElementById('apply-filters');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', function() {
      renderProductList();
    });
  }

  // Reset filters button
  const resetFiltersBtn = document.getElementById('reset-filters');
  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', function() {
      // Clear all filter inputs
      document.getElementById('product-search').value = '';
      document.getElementById('category-filter').value = '';
      document.getElementById('sentiment-filter').value = '';
      renderProductList();
    });
  }

  // Category and sentiment filter change events
  const categoryFilter = document.getElementById('category-filter');
  const sentimentFilter = document.getElementById('sentiment-filter');

  if (categoryFilter) {
    categoryFilter.addEventListener('change', function() {
      renderProductList();
    });
  }

  if (sentimentFilter) {
    sentimentFilter.addEventListener('change', function() {
      renderProductList();
    });
  }

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