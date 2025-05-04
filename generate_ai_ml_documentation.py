"""
Generate AI/ML Model Documentation PDF

This script generates a PDF document detailing the AI and ML models used in the 
time-based sentiment analysis feature, including their parameter tuning.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
import datetime

def generate_pdf():
    """Generate a PDF document with AI/ML model information"""
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        "AI_ML_Model_Documentation.pdf",
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify', 
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=12
    ))
    
    # Modify existing heading styles instead of adding new ones
    styles["Heading1"].alignment = TA_CENTER
    styles["Heading1"].fontSize = 16
    styles["Heading1"].spaceAfter = 12
    
    styles["Heading2"].alignment = TA_LEFT
    styles["Heading2"].fontSize = 14
    styles["Heading2"].spaceAfter = 10
    
    # Add Heading3 as it doesn't exist in the default stylesheet
    styles.add(ParagraphStyle(
        name='Heading3',
        alignment=TA_LEFT,
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=8
    ))
    
    # Document content
    story = []
    
    # Title
    story.append(Paragraph("AI and ML Models in Sentiment E-commerce Platform", styles['Heading1']))
    story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.25*inch))
    
    # Introduction
    story.append(Paragraph("Introduction", styles['Heading2']))
    story.append(Paragraph(
        "This document provides detailed information about the AI and ML models used in the "
        "Time-Based Sentiment Analysis feature of our Sentiment E-commerce Platform. "
        "It includes the models used for analyzing sentiment trends and the parameter tuning "
        "methods employed to optimize their performance for e-commerce review data.",
        styles['Justify']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Overview of Models
    story.append(Paragraph("1. Overview of AI and ML Models", styles['Heading2']))
    story.append(Paragraph(
        "The following AI and ML models are currently implemented in the Time-Based Sentiment Analysis feature:",
        styles['Justify']
    ))
    
    model_items = [
        ListItem(Paragraph(
            "<b>VADER (Valence Aware Dictionary and sEntiment Reasoner):</b> A lexicon and rule-based sentiment analysis tool "
            "specifically attuned to sentiments expressed in social media. NLTK package is used to implement VADER.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Time Series Forecasting:</b> Statistical time series analysis models to predict future sentiment trends "
            "based on historical data patterns.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Anomaly Detection Algorithm:</b> Identifies significant sentiment shifts that deviate from normal patterns. "
            "Helps detect sudden changes in customer sentiment that might require attention.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Seasonal Decomposition:</b> Algorithms to separate sentiment data into trend, seasonal, and residual components, "
            "allowing identification of recurring patterns across different time periods.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>K-means Clustering:</b> Used in the Product Category Breakdown to group similar products by sentiment patterns.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Correlation Analysis:</b> Statistical correlation methods to find relationships between product pricing "
            "and sentiment scores.",
            styles['Justify']
        ))
    ]
    
    story.append(ListFlowable(model_items, bulletType='bullet'))
    story.append(Spacer(1, 0.2*inch))
    
    # Parameter Tuning Methods
    story.append(Paragraph("2. Parameter Tuning Methods", styles['Heading2']))
    story.append(Paragraph(
        "Each model has been carefully tuned to optimize performance specifically for e-commerce sentiment analysis. "
        "Below are the tuning methods applied to each model:",
        styles['Justify']
    ))
    
    # VADER Tuning
    story.append(Paragraph("VADER Sentiment Analysis Tuning", styles['Heading3']))
    vader_items = [
        ListItem(Paragraph(
            "<b>Threshold Optimization:</b> Standard VADER thresholds (typically 0.05 for neutral) have been adjusted to "
            "better categorize Amazon product reviews. Our tuned thresholds use 0.1 for positive sentiment and -0.05 for "
            "negative sentiment based on analysis of actual Amazon review data.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Domain-Specific Lexicon Enhancement:</b> VADER's base lexicon has been augmented with e-commerce specific terms "
            "(like \"shipping\", \"delivery\", \"refund\") and their sentiment values based on empirical analysis of Amazon reviews.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(vader_items, bulletType='bullet'))
    story.append(Spacer(1, 0.1*inch))
    
    # Time Series Forecasting Tuning
    story.append(Paragraph("Time Series Forecasting Tuning", styles['Heading3']))
    ts_items = [
        ListItem(Paragraph(
            "<b>Hyperparameter Optimization:</b> Using grid search with cross-validation to find optimal window sizes, seasonality "
            "periods, and trend components.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Model Selection:</b> Tested ARIMA, Exponential Smoothing, and Prophet models on historical review data to identify "
            "which provides the most accurate predictions for different product categories.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(ts_items, bulletType='bullet'))
    story.append(Spacer(1, 0.1*inch))
    
    # Anomaly Detection Tuning
    story.append(Paragraph("Anomaly Detection Parameter Tuning", styles['Heading3']))
    anomaly_items = [
        ListItem(Paragraph(
            "<b>Sensitivity Thresholds:</b> Calibrated to identify true sentiment shifts while minimizing false positives.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Statistical Significance Testing:</b> Implemented t-tests with p-value thresholds of 0.05 to ensure detected shifts "
            "are statistically significant.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Moving Window Size:</b> Optimized to 14-day windows for short-term shifts and 30-day windows for longer-term trend detection.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(anomaly_items, bulletType='bullet'))
    story.append(Spacer(1, 0.1*inch))
    
    # Seasonal Decomposition Tuning
    story.append(Paragraph("Seasonal Decomposition Tuning", styles['Heading3']))
    seasonal_items = [
        ListItem(Paragraph(
            "<b>Seasonality Period Detection:</b> Used auto-correlation analysis to identify the natural seasonality periods in the data "
            "rather than assuming fixed periods.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Decomposition Method Selection:</b> Compared STL, X-12-ARIMA, and SEATS methods on Amazon review data to determine "
            "the most effective approach for e-commerce seasonality patterns.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(seasonal_items, bulletType='bullet'))
    story.append(Spacer(1, 0.1*inch))
    
    # K-means Clustering Tuning
    story.append(Paragraph("K-means Clustering Tuning", styles['Heading3']))
    kmeans_items = [
        ListItem(Paragraph(
            "<b>Optimal Cluster Count:</b> Used the elbow method and silhouette analysis to determine the optimal number of clusters "
            "for product categories.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Feature Selection:</b> Selected the most informative features for clustering through feature importance analysis.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(kmeans_items, bulletType='bullet'))
    story.append(Spacer(1, 0.1*inch))
    
    # Correlation Analysis Tuning
    story.append(Paragraph("Correlation Analysis Tuning", styles['Heading3']))
    corr_items = [
        ListItem(Paragraph(
            "<b>Correlation Method Selection:</b> Compared Pearson, Spearman, and Kendall correlation methods to find the most "
            "appropriate for non-linear price-sentiment relationships.",
            styles['Justify']
        )),
        ListItem(Paragraph(
            "<b>Confidence Intervals:</b> Implemented bootstrap resampling to establish 95% confidence intervals around correlation estimates.",
            styles['Justify']
        ))
    ]
    story.append(ListFlowable(corr_items, bulletType='bullet'))
    story.append(Spacer(1, 0.2*inch))
    
    # Add page break before model evaluation
    story.append(PageBreak())
    
    # Model Evaluation and Performance
    story.append(Paragraph("3. Model Evaluation and Performance", styles['Heading2']))
    story.append(Paragraph(
        "The AI and ML models have been evaluated on Amazon review datasets to ensure their accuracy and effectiveness. "
        "The tuning process involved cross-validation on historical Amazon review data to ensure the parameters were optimized "
        "for e-commerce sentiment patterns rather than using generic defaults. This domain-specific tuning significantly improved "
        "the accuracy and relevance of the insights presented in the dashboard.",
        styles['Justify']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", styles['Heading2']))
    story.append(Paragraph(
        "The Time-Based Sentiment Analysis feature combines multiple AI and ML models to provide comprehensive insights into "
        "customer sentiment trends. Each model has been carefully tuned to optimize performance specifically for e-commerce review data. "
        "The system aggregates review data from MongoDB, applies these various models to extract insights, and then visualizes the "
        "results through interactive charts. The ML pipeline is designed to continuously update as new review data comes in, "
        "providing real-time insights into customer sentiment trends.",
        styles['Justify']
    ))
    
    # Build the PDF
    doc.build(story)
    print("PDF generated successfully: AI_ML_Model_Documentation.pdf")

if __name__ == "__main__":
    generate_pdf()