import math
import pytest

from src.services.TwitterConnection import TwitterConnection
from src.services.SentAnalysis import SentAnalysis

twitter_conn = TwitterConnection()


def test_sentiment_polarity():
    req_str = 'Ohio (derailment OR accident OR trains OR chemicals OR chernobyl OR disaster)'
    df_tweets = twitter_conn.search_recent(req_str)
    sentiment = SentAnalysis()
    tweets = df_tweets.to_dict(orient='records')

    if not tweets:
        pytest.fail("No tweets found in the search result.")

    first_tweet = tweets[0]
    data = sentiment.sentiment_fit(first_tweet, "text")

    assert data, "Error in Twitter Sentiment Result: Dict is empty"

    assert_sentiment_data(data)


def assert_sentiment_data(data):
    assert 'sentiment' in data, "Error in Twitter Sentiment: Result is missing sentiment"
    assert data['sentiment'], "Error in Twitter Sentiment: Sentiment is empty"

    assert 'sentiment_score' in data, "Error in Twitter Sentiment: Score is missing"
    assert data['sentiment_score'] is not None, "Error in Twitter Sentiment: Score is null"

    assert 'sentiment_words' in data, "Error in Twitter Sentiment: Words are missing"
    assert data['sentiment_words'], "Error in Twitter Sentiment: Words are empty"

    assert_score_not_nan(data, 'neg_score', "Negative")
    assert_score_not_nan(data, 'neu_score', "Neutral")
    assert_score_not_nan(data, 'pos_score', "Positive")


def assert_score_not_nan(data, score_key, score_name):
    assert score_key in data, f"Error in Twitter Sentiment: {score_name} Score is missing"
    assert data[score_key] is not None and not math.isnan(
        data[score_key]), f"Error in Twitter Sentiment: {score_name} Score is null or NaN"
