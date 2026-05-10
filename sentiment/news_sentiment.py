from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download the required AI data (only needs to be done once)
nltk.download('vader_lexicon')

def analyze_news_sentiment(headlines):
    """
    Analyzes a list of headlines and returns a score from -1 (Bad) to 1 (Good).
    """
    sia = SentimentIntensityAnalyzer()
    total_score = 0
    
    if not headlines:
        return 0 # Neutral if no news
    
    for news in headlines:
        # Get the 'compound' score which is the overall mood
        score = sia.polarity_scores(news)['compound']
        total_score += score
        
    avg_score = total_score / len(headlines)
    
    # Logic for your bot
    if avg_score >= 0.05:
        return "POSITIVE"
    elif avg_score <= -0.05:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

# Test Example
# test_headlines = ["Reliance profits jump 20%", "Market crash expected soon"]
# print(analyze_news_sentiment(test_headlines))