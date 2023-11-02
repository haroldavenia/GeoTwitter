import pytest
import math

from src.services.TwitterConnection import TwitterConnection
from src.services.ExtractLocation import ExtractLocation
from src.utils.Log import Log

twitter_conn = TwitterConnection()
log = Log()


def test_extract_loc():
    req_str = 'Ohio (derailment OR accident OR trains OR chemicals OR chernobyl OR disaster)'
    df_tweets = twitter_conn.search_recent(req_str)
    tweets = df_tweets.to_dict(orient='records')

    if not tweets:
        pytest.fail("No tweets found in the search result.")

    first_tweet = tweets[0]
    extract_loc = ExtractLocation(first_tweet, twitter_conn, log)
    extract_loc.extract()
    data = extract_loc.get_location()

    assert data, "Error in Twitter Extract Location: Location is empty"


def assert_location_data(data):
    assert 'geometry' in data, "Error in Twitter Extract Location: Result is missing geometry"
    assert data['geometry'], "Error in Twitter Extract Location: geometry is empty"

    assert 'x' in data, "Error in Twitter Extract Location: X coordinate is missing"
    assert data['x'] is not None, "Error in Twitter Extract Location: X coordinate is null"

    assert 'y' in data, "Error in Twitter Extract Location: Y coordinate is missing"
    assert data['y'] is not None, "Error in Twitter Extract Location: Y coordinate is null"

    assert 'accuracy' in data, f"Error in Twitter Extract Location: accuracy is missing"
    assert data['accuracy'] is not None and not math.isnan(
        data['accuracy']), f"Error in Twitter Sentiment: accuracy is null or NaN"

