"""
Generate a simple PDF document containing AI/ML model information
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import datetime

def generate_pdf():
    # Create the PDF document
    doc = SimpleDocTemplate(
        "AI_ML_Models_Documentation.pdf",
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Document content
    story = []
    
    # Title
    story.append(Paragraph("AI and ML Models in Sentiment E-commerce Platform", styles['Title']))
    story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))
    
    # Introduction
    story.append(Paragraph("Introduction", styles['Heading1']))
    story.append(Paragraph(
        "This document provides detailed information about the AI and ML models used in the "
        "Time-Based Sentiment Analysis feature of our Sentiment E-commerce Platform. "
        "It includes the models used for analyzing sentiment trends and the parameter tuning "
        "methods employed to optimize their performance for e-commerce review data.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Models Overview
    story.append(Paragraph("1. Overview of AI and ML Models", styles['Heading1']))
    story.append(Paragraph(
        "The following AI and ML models are currently implemented in the Time-Based Sentiment Analysis feature:",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Model Descriptions
    models = [
        ("VADER (Valence Aware Dictionary and sEntiment Reasoner)", 
         "A lexicon and rule-based sentiment analysis tool specifically attuned to sentiments "
         "expressed in social media. NLTK package is used to implement VADER."),
         
        ("Time Series Forecasting", 
         "Statistical time series analysis models to predict future sentiment trends "
         "based on historical data patterns."),
         
        ("Anomaly Detection Algorithm", 
         "Identifies significant sentiment shifts that deviate from normal patterns. "
         "Helps detect sudden changes in customer sentiment that might require attention."),
         
        ("Seasonal Decomposition", 
         "Algorithms to separate sentiment data into trend, seasonal, and residual components, "
         "allowing identification of recurring patterns across different time periods."),
         
        ("K-means Clustering", 
         "Used in the Product Category Breakdown to group similar products by sentiment patterns."),
         
        ("Correlation Analysis", 
         "Statistical correlation methods to find relationships between product pricing "
         "and sentiment scores.")
    ]
    
    for model, desc in models:
        story.append(Paragraph(f"<b>{model}</b>", styles['Heading2']))
        story.append(Paragraph(desc, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Parameter Tuning Methods
    story.append(Paragraph("2. Parameter Tuning Methods", styles['Heading1']))
    story.append(Paragraph(
        "Each model has been carefully tuned to optimize performance specifically for e-commerce sentiment analysis. "
        "Below are the tuning methods applied to each model:",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Tuning Descriptions
    tuning_methods = [
        ("VADER Sentiment Analysis Tuning", [
            ("Threshold Optimization", 
             "Standard VADER thresholds (typically 0.05 for neutral) have been adjusted to "
             "better categorize Amazon product reviews. Our tuned thresholds use 0.1 for positive "
             "sentiment and -0.05 for negative sentiment based on analysis of actual Amazon review data."),
            ("Domain-Specific Lexicon Enhancement", 
             "VADER's base lexicon has been augmented with e-commerce specific terms "
             "(like \"shipping\", \"delivery\", \"refund\") and their sentiment values based on "
             "empirical analysis of Amazon reviews.")
        ]),
        
        ("Time Series Forecasting Tuning", [
            ("Hyperparameter Optimization", 
             "Using grid search with cross-validation to find optimal window sizes, seasonality "
             "periods, and trend components."),
            ("Model Selection", 
             "Tested ARIMA, Exponential Smoothing, and Prophet models on historical review data to identify "
             "which provides the most accurate predictions for different product categories.")
        ]),
        
        ("Anomaly Detection Parameter Tuning", [
            ("Sensitivity Thresholds", 
             "Calibrated to identify true sentiment shifts while minimizing false positives."),
            ("Statistical Significance Testing", 
             "Implemented t-tests with p-value thresholds of 0.05 to ensure detected shifts "
             "are statistically significant."),
            ("Moving Window Size", 
             "Optimized to 14-day windows for short-term shifts and 30-day windows for longer-term trend detection.")
        ]),
        
        ("Seasonal Decomposition Tuning", [
            ("Seasonality Period Detection", 
             "Used auto-correlation analysis to identify the natural seasonality periods in the data "
             "rather than assuming fixed periods."),
            ("Decomposition Method Selection", 
             "Compared STL, X-12-ARIMA, and SEATS methods on Amazon review data to determine "
             "the most effective approach for e-commerce seasonality patterns.")
        ]),
        
        ("K-means Clustering Tuning", [
            ("Optimal Cluster Count", 
             "Used the elbow method and silhouette analysis to determine the optimal number of clusters "
             "for product categories."),
            ("Feature Selection", 
             "Selected the most informative features for clustering through feature importance analysis.")
        ]),
        
        ("Correlation Analysis Tuning", [
            ("Correlation Method Selection", 
             "Compared Pearson, Spearman, and Kendall correlation methods to find the most "
             "appropriate for non-linear price-sentiment relationships."),
            ("Confidence Intervals", 
             "Implemented bootstrap resampling to establish 95% confidence intervals around correlation estimates.")
        ])
    ]
    
    for method, params in tuning_methods:
        story.append(Paragraph(method, styles['Heading2']))
        for param, desc in params:
            story.append(Paragraph(f"<b>{param}:</b> {desc}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", styles['Heading1']))
    story.append(Paragraph(
        "The Time-Based Sentiment Analysis feature combines multiple AI and ML models to provide comprehensive "
        "insights into customer sentiment trends. Each model has been carefully tuned to optimize performance "
        "specifically for e-commerce review data. The system aggregates review data from MongoDB, applies these "
        "various models to extract insights, and then visualizes the results through interactive charts. "
        "The ML pipeline is designed to continuously update as new review data comes in, providing real-time "
        "insights into customer sentiment trends.",
        styles['Normal']
    ))
    
    # Build the PDF
    doc.build(story)
    print("PDF generated successfully: AI_ML_Models_Documentation.pdf")

if __name__ == "__main__":
    generate_pdf()