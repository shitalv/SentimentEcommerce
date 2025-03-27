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
    Identify keywords contributing to sentiment - Amazon review style analysis
    """
    # Improved keyword extraction based on Amazon review analysis patterns
    words = text.lower().split()
    
    # Common Amazon review sentiment keywords (extended for better coverage)
    positive_keywords = {
        # Product quality
        "quality": ["high quality", "well made", "durable", "sturdy", "solid", "premium"],
        
        # Performance
        "performance": ["fast", "smooth", "efficient", "effective", "powerful", "responsive"],
        
        # Value
        "value": ["worth", "value", "bargain", "affordable", "reasonable price"],
        
        # User experience
        "experience": ["easy to use", "user friendly", "intuitive", "convenient", "comfortable"],
        
        # Satisfaction
        "satisfaction": ["love", "perfect", "excellent", "amazing", "awesome", "great", "fantastic", 
                         "outstanding", "happy", "satisfied", "impressed", "recommend"]
    }
    
    negative_keywords = {
        # Product quality
        "quality": ["poor quality", "cheaply made", "flimsy", "fragile", "broke", "low quality"],
        
        # Performance
        "performance": ["slow", "sluggish", "lags", "underperforms", "weak", "unresponsive"],
        
        # Value
        "value": ["overpriced", "expensive", "not worth", "waste of money", "pricey"],
        
        # User experience
        "experience": ["difficult to use", "complicated", "confusing", "inconvenient", "uncomfortable"],
        
        # Dissatisfaction
        "dissatisfaction": ["disappointed", "frustrating", "terrible", "horrible", "awful", "bad", 
                            "poor", "worst", "hate", "annoying", "regret", "avoid", "return"]
    }
    
    # Extract phrases, not just individual words
    text_lower = text.lower()
    
    extracted_keywords = []
    
    if sentiment_class == "positive":
        for category, keywords in positive_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the context (5 words around the keyword)
                    words = text_lower.split()
                    if len(keyword.split()) == 1:  # Single word
                        if keyword in words:
                            idx = words.index(keyword)
                            start = max(0, idx - 3)
                            end = min(len(words), idx + 3)
                            context = " ".join(words[start:end])
                            extracted_keywords.append({"keyword": keyword, "category": category, "context": context})
                    else:  # Multi-word phrase
                        extracted_keywords.append({"keyword": keyword, "category": category})
    
    elif sentiment_class == "negative":
        for category, keywords in negative_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the context (5 words around the keyword)
                    words = text_lower.split()
                    if len(keyword.split()) == 1:  # Single word
                        if keyword in words:
                            idx = words.index(keyword)
                            start = max(0, idx - 3)
                            end = min(len(words), idx + 3)
                            context = " ".join(words[start:end])
                            extracted_keywords.append({"keyword": keyword, "category": category, "context": context})
                    else:  # Multi-word phrase
                        extracted_keywords.append({"keyword": keyword, "category": category})
    
    # Return unique keywords
    unique_keywords = []
    seen = set()
    for kw in extracted_keywords:
        if kw["keyword"] not in seen:
            unique_keywords.append(kw)
            seen.add(kw["keyword"])
    
    return unique_keywords
