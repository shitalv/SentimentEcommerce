import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import ProductList from './components/ProductList';
import ProductDetail from './components/ProductDetail';
import SearchFilter from './components/SearchFilter';

function App() {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [categories, setCategories] = useState([]);

  // Fetch products from the backend
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        // Use relative URL to match both development and production
        const apiUrl = '/api/products';
        const response = await axios.get(apiUrl);
        setProducts(response.data);
        setFilteredProducts(response.data);
        
        // Extract unique categories
        const uniqueCategories = [...new Set(response.data.map(product => product.category))];
        setCategories(uniqueCategories);
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch products. Please try again later.');
        setLoading(false);
        console.error('Error fetching products:', err);
      }
    };

    fetchProducts();
  }, []);

  // Apply filters when search term, sentiment filter, or category filter changes
  useEffect(() => {
    if (products.length === 0) return;

    let filtered = [...products];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(product => 
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sentiment filter
    if (sentimentFilter !== 'all') {
      filtered = filtered.filter(product => {
        if (sentimentFilter === 'positive') return product.sentiment_score >= 0.5;
        if (sentimentFilter === 'neutral') return product.sentiment_score >= 0.3 && product.sentiment_score < 0.5;
        if (sentimentFilter === 'negative') return product.sentiment_score < 0.3;
        return true;
      });
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(product => product.category === categoryFilter);
    }

    setFilteredProducts(filtered);
  }, [searchTerm, sentimentFilter, categoryFilter, products]);

  const handleProductSelect = async (productId) => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/products/${productId}`);
      setSelectedProduct(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch product details. Please try again later.');
      setLoading(false);
      console.error('Error fetching product details:', err);
    }
  };

  const handleBackToProducts = () => {
    setSelectedProduct(null);
  };

  return (
    <div className="App">
      <Navbar />
      <main className="container py-4">
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {selectedProduct ? (
          <ProductDetail product={selectedProduct} onBack={handleBackToProducts} />
        ) : (
          <>
            <h1 className="mb-4">Product Insights with Sentiment Analysis</h1>
            <SearchFilter 
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
              sentimentFilter={sentimentFilter}
              setSentimentFilter={setSentimentFilter}
              categoryFilter={categoryFilter}
              setCategoryFilter={setCategoryFilter}
              categories={categories}
            />
            
            {loading ? (
              <div className="text-center my-5">
                <div className="spinner-border" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : (
              <ProductList 
                products={filteredProducts} 
                onSelectProduct={handleProductSelect} 
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
