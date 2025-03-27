import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging
import re
import os

# Set NLTK data path to current directory to ensure write permissions
nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
nltk.data.path.insert(0, nltk_data_dir)

# Download required NLTK resources
try:
    nltk.data.find('vader_lexicon')
    logging.info("VADER lexicon already downloaded")
except LookupError:
    logging.info("Downloading VADER lexicon for sentiment analysis")
    nltk.download('vader_lexicon', download_dir=nltk_data_dir)

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

def preprocess_text(text):
    """
    Preprocess text for sentiment analysis
    - Convert to lowercase
    - Remove special characters
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    return text.strip()

def analyze_sentiment(text):
    """
    Analyze sentiment of text using NLTK's VADER
    Returns a score between 0 and 1, where:
    - 0-0.3: Negative
    - 0.3-0.5: Neutral
    - 0.5-1.0: Positive
    """
    try:
        # Preprocess text
        cleaned_text = preprocess_text(text)
        
        if not cleaned_text:
            return 0.5  # Neutral score for empty text
        
        # Get sentiment scores
        sentiment_scores = sia.polarity_scores(cleaned_text)
        
        # Convert the compound score from [-1, 1] to [0, 1]
        normalized_score = (sentiment_scores['compound'] + 1) / 2
        
        return normalized_score
    except Exception as e:
        logging.error(f"Error in sentiment analysis: {str(e)}")
        return 0.5  # Return neutral sentiment on error

def classify_sentiment(score):
    """
    Classify sentiment score into positive, neutral, or negative
    """
    if score >= 0.5:
        return "positive"
    elif score >= 0.3:
        return "neutral"
    else:
        return "negative"

def get_sentiment_keywords(text, sentiment_class):
    """
    Identify keywords contributing to sentiment
    """
    # This is a simplified implementation
    # A more sophisticated approach would involve NLP techniques
    # to identify influential words in sentiment determination
    words = text.lower().split()
    
    if sentiment_class == "positive":
        positive_words = ["good", "great", "excellent", "amazing", "love", "best", "perfect"]
        return [word for word in words if word in positive_words]
    elif sentiment_class == "negative":
        negative_words = ["bad", "poor", "terrible", "worst", "hate", "disappointing", "failed"]
        return [word for word in words if word in negative_words]
    else:
        return []
