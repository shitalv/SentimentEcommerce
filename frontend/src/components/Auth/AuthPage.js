import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

function AuthPage({ onAuthSuccess }) {
  const [showLogin, setShowLogin] = useState(true);

  const handleLogin = (user) => {
    onAuthSuccess(user);
  };

  const handleRegister = (user) => {
    onAuthSuccess(user);
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="text-center mb-4">
            <h2>Sentiment-Driven Product Insights</h2>
            <p className="lead">Discover what customers really think about products</p>
          </div>
          
          {showLogin ? (
            <LoginForm 
              onLogin={handleLogin} 
              onSwitchToRegister={() => setShowLogin(false)}
            />
          ) : (
            <RegisterForm 
              onRegister={handleRegister} 
              onSwitchToLogin={() => setShowLogin(true)}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default AuthPage;