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

def analyze_hype_vs_reality(product_description, reviews):
    """
    Compare marketing claims in product description against actual user experiences
    Returns a dictionary with matching and contradicting claims
    """
    if not product_description or not reviews:
        return {
            "matches": [],
            "contradictions": [],
            "marketing_claims": []
        }
    
    # Common marketing claim patterns
    marketing_phrases = [
        "best", "perfect", "ultimate", "revolutionary", "game-changing",
        "innovative", "premium", "high-quality", "top-rated", "professional",
        "durable", "long-lasting", "easy to use", "maintenance-free", "efficient",
        "highest rated", "best-selling", "unmatched", "incomparable", "superior",
        "advanced", "state-of-the-art", "cutting-edge", "next-generation",
        "breakthrough", "world-class", "top-of-the-line", "industry-leading",
        "reliable", "exceptional", "outstanding", "excellent"
    ]
    
    # Extract marketing claims from product description
    description_lower = product_description.lower()
    marketing_claims = []
    
    for phrase in marketing_phrases:
        if phrase in description_lower:
            # Find the context (10 words around the marketing phrase)
            words = description_lower.split()
            if phrase in words:
                try:
                    idx = words.index(phrase)
                    start = max(0, idx - 5)
                    end = min(len(words), idx + 5)
                    context = " ".join(words[start:end])
                    marketing_claims.append({
                        "claim": phrase,
                        "context": context
                    })
                except ValueError:
                    # Handle phrases with multiple words
                    for i in range(len(words) - len(phrase.split()) + 1):
                        if " ".join(words[i:i+len(phrase.split())]) == phrase:
                            start = max(0, i - 5)
                            end = min(len(words), i + len(phrase.split()) + 5)
                            context = " ".join(words[start:end])
                            marketing_claims.append({
                                "claim": phrase,
                                "context": context
                            })
                            break
            else:
                # Handle multi-word phrases
                for i in range(len(words) - 1):
                    if " ".join(words[i:i+2]) == phrase:
                        start = max(0, i - 5)
                        end = min(len(words), i + 7)
                        context = " ".join(words[start:end])
                        marketing_claims.append({
                            "claim": phrase,
                            "context": context
                        })
                        break
    
    # Check reviews for confirmation or contradiction of claims
    matches = []
    contradictions = []
    
    for claim in marketing_claims:
        claim_phrase = claim["claim"]
        
        # Look for positive confirmations and negative contradictions
        confirmations = 0
        denials = 0
        
        for review in reviews:
            review_text = review.get("text", "").lower()
            sentiment = review.get("sentiment", 0.5)
            
            # Check if the claim phrase appears in the review
            if claim_phrase in review_text:
                if sentiment >= 0.5:  # Positive review
                    confirmations += 1
                else:  # Negative review
                    denials += 1
            
            # Check for explicit contradictions (e.g., "not durable" if claim is "durable")
            contradiction_patterns = [
                f"not {claim_phrase}", f"isn't {claim_phrase}", f"isnt {claim_phrase}",
                f"doesn't {claim_phrase}", f"doesnt {claim_phrase}", f"far from {claim_phrase}",
                f"barely {claim_phrase}", f"hardly {claim_phrase}", f"wasn't {claim_phrase}",
                f"wasnt {claim_phrase}", f"not very {claim_phrase}", f"not really {claim_phrase}"
            ]
            
            for pattern in contradiction_patterns:
                if pattern in review_text:
                    denials += 1
        
        # Determine if the claim is matched or contradicted
        if confirmations > 0 and confirmations > denials:
            matches.append({
                "claim": claim_phrase,
                "context": claim["context"],
                "confirmations": confirmations,
                "denials": denials
            })
        elif denials > 0:
            contradictions.append({
                "claim": claim_phrase,
                "context": claim["context"],
                "confirmations": confirmations,
                "denials": denials
            })
    
    return {
        "matches": matches,
        "contradictions": contradictions,
        "marketing_claims": marketing_claims
    }
