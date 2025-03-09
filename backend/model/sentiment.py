import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re

# Download necessary resources
nltk.download('vader_lexicon')

# Initialize Sentiment Intensity Analyzer
sia = SentimentIntensityAnalyzer()

# List of mental health-related keywords
MENTAL_HEALTH_KEYWORDS = [
    'depressed', 'anxious', 'hopeless', 'tired', 'sad', 'lonely', 'worthless',
    'angry', 'stressed', 'fear', 'panic', 'suicidal', 'happy', 'excited', 'relaxed'
]

def preprocess_text(text):
    """Cleans and preprocesses the conversation text."""
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def analyze_sentiment(text):
    """Performs sentiment analysis on the text."""
    sentiment = sia.polarity_scores(text)
    return sentiment

def detect_keywords(text, keywords):
    """Detects presence of mental health-related keywords."""
    found_keywords = [word for word in keywords if word in text]
    return found_keywords

def assess_mental_health(conversation):
    """Assesses mental health based on sentiment and keywords."""
    processed_text = preprocess_text(conversation)
    sentiment = analyze_sentiment(processed_text)
    keywords_found = detect_keywords(processed_text, MENTAL_HEALTH_KEYWORDS)

    assessment = {
        'Sentiment': sentiment,
        'Keywords Found': keywords_found,
        'Assessment': ''
    }

    if sentiment['compound'] <= -0.5 or any(word in ['suicidal', 'hopeless', 'worthless'] for word in keywords_found):
        assessment['Assessment'] = 'High risk. Immediate intervention recommended.'
    elif sentiment['compound'] < 0:
        assessment['Assessment'] = 'Moderate risk. Monitor and offer support.'
    else:
        assessment['Assessment'] = 'Low risk. No immediate action needed.'

    return sentiment['compound']


