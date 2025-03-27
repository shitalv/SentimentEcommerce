import React from 'react';

function HypeVsRealityCheck({ hypeData }) {
  if (!hypeData || (!hypeData.contradictions.length && !hypeData.matches.length)) {
    return (
      <div className="card mb-4">
        <div className="card-header">
          <h5>Hype vs. Reality Check</h5>
        </div>
        <div className="card-body">
          <p className="text-muted">No marketing claims were found to analyze</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="card mb-4">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">
          <i className="fas fa-balance-scale me-2"></i>
          Hype vs. Reality Check
        </h5>
      </div>
      <div className="card-body">
        <p className="lead">
          We've analyzed this product's marketing claims against actual customer reviews.
        </p>
        
        {/* Marketing Claims Alert */}
        {hypeData.marketing_claims.length > 0 && (
          <div className="alert alert-secondary mb-3">
            <h6 className="mb-2">
              <i className="fas fa-bullhorn me-2"></i>
              Marketing Claims Detected:
            </h6>
            <ul className="mb-0">
              {hypeData.marketing_claims.map((claim, idx) => (
                <li key={idx}>
                  "<strong>{claim.claim}</strong>" - <span className="text-muted fst-italic">"{claim.context}"</span>
                </li>
              )).slice(0, 5)}
              {hypeData.marketing_claims.length > 5 && (
                <li className="text-muted">...and {hypeData.marketing_claims.length - 5} more</li>
              )}
            </ul>
          </div>
        )}
        
        <div className="row g-3">
          {/* Confirmed Claims */}
          <div className="col-md-6">
            <div className="card h-100 border-success">
              <div className="card-header bg-success text-white">
                <h6 className="mb-0">
                  <i className="fas fa-check-circle me-2"></i>
                  Confirmed in Reviews
                </h6>
              </div>
              <div className="card-body">
                {hypeData.matches.length > 0 ? (
                  <ul className="list-group list-group-flush">
                    {hypeData.matches.map((match, idx) => (
                      <li key={idx} className="list-group-item d-flex justify-content-between align-items-start">
                        <div className="ms-2 me-auto">
                          <div className="fw-bold">{match.claim}</div>
                          <small className="text-muted">From description: "{match.context}"</small>
                        </div>
                        <span className="badge bg-success rounded-pill" title={`${match.confirmations} confirming reviews`}>
                          {match.confirmations} <i className="fas fa-thumbs-up ms-1"></i>
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted">
                    No marketing claims were confirmed by reviewers
                  </p>
                )}
              </div>
            </div>
          </div>
          
          {/* Contradicted Claims */}
          <div className="col-md-6">
            <div className="card h-100 border-danger">
              <div className="card-header bg-danger text-white">
                <h6 className="mb-0">
                  <i className="fas fa-exclamation-circle me-2"></i>
                  Contradicted in Reviews
                </h6>
              </div>
              <div className="card-body">
                {hypeData.contradictions.length > 0 ? (
                  <ul className="list-group list-group-flush">
                    {hypeData.contradictions.map((contradiction, idx) => (
                      <li key={idx} className="list-group-item d-flex justify-content-between align-items-start">
                        <div className="ms-2 me-auto">
                          <div className="fw-bold text-danger">{contradiction.claim}</div>
                          <small className="text-muted">From description: "{contradiction.context}"</small>
                        </div>
                        <span className="badge bg-danger rounded-pill" title={`${contradiction.denials} contradicting reviews`}>
                          {contradiction.denials} <i className="fas fa-thumbs-down ms-1"></i>
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted">
                    No marketing claims were contradicted by reviewers
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Reality Score */}
        {(hypeData.matches.length > 0 || hypeData.contradictions.length > 0) && (
          <div className="mt-3 text-center">
            <h6>Reality Score</h6>
            {(() => {
              const totalClaims = hypeData.matches.length + hypeData.contradictions.length;
              const confirmationRate = totalClaims > 0 ? (hypeData.matches.length / totalClaims) * 100 : 0;
              
              let badgeClass = "bg-danger";
              let badgeText = "Poor";
              
              if (confirmationRate >= 90) {
                badgeClass = "bg-success";
                badgeText = "Excellent";
              } else if (confirmationRate >= 70) {
                badgeClass = "bg-primary";
                badgeText = "Good";
              } else if (confirmationRate >= 50) {
                badgeClass = "bg-warning text-dark";
                badgeText = "Fair";
              }
              
              return (
                <div className="progress" style={{height: "30px"}}>
                  <div 
                    className={`progress-bar ${badgeClass}`} 
                    role="progressbar" 
                    style={{width: `${confirmationRate}%`}} 
                    aria-valuenow={confirmationRate} 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  >
                    <strong>{badgeText} ({Math.round(confirmationRate)}%)</strong>
                  </div>
                </div>
              );
            })()}
            <small className="text-muted d-block mt-1">
              Based on how well marketing claims match customer experiences
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default HypeVsRealityCheck;