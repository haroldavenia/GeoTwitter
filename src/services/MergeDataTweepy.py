import pandas as pd


class MergeTweetsData(object):
    _data = None
    _df_data = None
    _tweet_fields = ['created_at', 'geo', 'id', 'text', 'author_id', 'coordinates', 'place']
    _user_fields = ['location', 'description', 'name', 'id', 'derived']

    def __init__(self, tweets):
        self._data = tweets
        self._df_data = self._merge(tweets)

    def _get_place_id(self, x):
        try:
            return x.get('place_id') if x else None
        except Exception as e:
            print(f"Error: {e}, Value: {x}")
            return None

    def _merge(self, tweets):
        df_tweets = pd.DataFrame(tweets.data)
        df_tweets = self._filter_col(self._tweet_fields, df_tweets)
        df_tweets = df_tweets.rename(columns={'id': 'conversation_id'})
        users_dict = tweets.includes.get('users', None)
        if users_dict:
            df_users = pd.DataFrame(users_dict)
            df_users = self._filter_col(self._user_fields, df_users)
            df_users = df_users.rename(columns={'id': 'id_user', 'location': 'user_loc', 'description': 'user_desc',
                                                'name': 'user_name', 'derived': 'user_derived'})
            df_tweets = pd.merge(df_tweets, df_users, left_on='author_id', right_on='id_user', how='left')
            df_tweets = df_tweets.drop(['id_user'], axis=1)
            df_tweets = df_tweets.fillna('')
            if 'geo' in df_tweets.columns:
                df_tweets['place_id'] = pd.Series(df_tweets['geo']).apply(self._get_place_id)
                places_dict = tweets.includes.get('places', None)
                if 'coordinates' in df_tweets.columns or 'place' in df_tweets.columns:
                    pass
                if places_dict:
                    df_places = pd.DataFrame([(place['id'], place.data) for place in places_dict],
                                             columns=['id_place', 'place'])
                    df_tweets = pd.merge(df_tweets, df_places, left_on='place_id', right_on='id_place', how='left')

        df_tweets = df_tweets.fillna('')
        return df_tweets

    def _filter_col(self, cols_name, df):
        cols_exist = list(set(cols_name).intersection(df.columns))
        return df[cols_exist]

    def get_dataframe(self):
        return self._df_data
