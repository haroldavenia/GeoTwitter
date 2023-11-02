import tweepy
from src.services.MergeDataTweepy import MergeTweetsData


class TwitterSearchError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TwitterConnection(object):
    _instance = None
    _client = None
    _api = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TwitterConnection, cls).__new__(cls, *args, **kwargs)
            # Aquí puedes realizar la configuración inicial de la conexión a Twitter.
            cls._instance._init()
        return cls._instance

    def _init(self):
        APP_KEY = 'geVCcpFGxa2d5w8w8v4ChQWSa'
        APP_SECRET = 'Z4QFq7rMykKWGuvVyQzpb1o8g3kbqEeSCygcHV0IPIJQYMmmK6'
        OAUTH_TOKEN = '1698885502286303232-MrysZ03bxt2CooRS43urRJdvNFby9y'
        OAUTH_TOKEN_SECRET = 'QmsndTiSgWHAHusssEY6oxHaTWD1NNJyF0wz0qOwK5DAJ'
        auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
        auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self._api = tweepy.API(auth)
        self._client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAACoepwEAAAAAYZxyi0OMnOipc5i4zdx1z3gUEro%3DYJAkB0'
                                                  'ye4Oi8QL5y7bjiqohrUQHeQ3jmhgyRVyD2Lk348pszlY')

    def search_recent(self, query):
        try:
            tweets = self._client.search_recent_tweets(query=query,
                                                       tweet_fields=['conversation_id', 'created_at', 'geo', 'id',
                                                                     'text', 'author_id'],
                                                       place_fields=['contained_within', 'country', 'country_code',
                                                                     'full_name', 'geo', 'id', 'name', 'place_type'],
                                                       user_fields=['location', 'description', 'name', 'username'],
                                                       expansions=['author_id', 'geo.place_id'],
                                                       max_results=100)
            merge_data = MergeTweetsData(tweets)
            return merge_data.get_dataframe()
        except tweepy.TweepyException as e:
            error_message = f"Error in Twitter search: {str(e)}"
            raise TwitterSearchError(error_message)

    def get_friends(self, user_id):
        return self._api.get_friends(user_id=user_id, count=50)

    def is_connected(self):
        try:
            self._api.verify_credentials()
            return True
        except:
            return False

    # def listener(self, query, opt):
    #     while True:
    #         try:
    #             tweets = self.search_recent(query)
    #             self.notify_observers(tweets, opt)
    #             time.sleep(30)
    #         except tweepy.TweepyException as e:
    #             error_message = f"Error in Twitter search: {str(e)}"
    #             raise TwitterSearchError(error_message)
    #             break
    #     return False
