import uuid
import pytz
from src.models.TwitterData import TwitterData
from datetime import datetime

FILTER_FIELDS = ['conversation_id', 'created_at', 'id', 'text', 'author_id', 'x', 'y', 'sentiment',
                 'sentiment_score', 'neg_score', 'neu_score', 'pos_score', 'neg_sent_words', 'pos_sent_words',
                 'neu_sent_words', 'neg_words_count', 'pos_words_count', 'neu_words_count']


class Repository(object):

    def __init__(self):
        pass

    @staticmethod
    def _filtered_dict(obj):
        return {k: v for (k, v) in obj.items() if k in FILTER_FIELDS}

    def save_db(self, twitters, opt):
        try:
            tenant_id = opt['client_id']
            tag_filter = opt['tag_filter']
            query_uuid = str(uuid.uuid4())
            date_saved = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
            TwitterData.save_db(tenant_id, query_uuid, tag_filter, twitters)
            return {
                "tenant_id": tenant_id,
                "query_uuid": query_uuid,
                "tag_filter": tag_filter,
                "date_saved": date_saved
            }
        except Exception as e:
            print(f"Error saving data to MongoDB: {e}")
