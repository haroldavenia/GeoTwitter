from mongoengine import Document, StringField, FloatField, IntField, DateTimeField, PointField
from datetime import datetime


class TwitterData(Document):
    tenant_id = StringField(required=True)
    query_uuid = StringField(required=True)
    tag_filter = StringField(required=True)
    date_saved = DateTimeField(required=True, default=datetime.utcnow)
    author_id = IntField(required=True)
    created_at = DateTimeField(required=True)
    conversation_id = IntField(required=True)
    text = StringField(required=True)
    x = FloatField(required=True)
    y = FloatField(required=True)
    lonlat = StringField(required=True)
    latlon = StringField(required=True)
    city = StringField(required=True)
    state = StringField(required=True)
    country = StringField(required=True)
    sentiment = StringField(required=True)
    sentiment_score = FloatField(required=True)
    neg_score = FloatField(required=True)
    neu_score = FloatField(required=True)
    pos_score = FloatField(required=True)
    neg_sent_words = StringField(required=True)
    pos_sent_words = StringField(required=True)
    neu_sent_words = StringField(required=True)
    neg_words_count = IntField(required=True)
    pos_words_count = IntField(required=True)
    neu_words_count = IntField(required=True)
    most_neg_word = StringField(required=True)
    most_pos_word = StringField(required=True)
    most_neu_word = StringField(required=True)
    sentiment_word = StringField(required=True)
    sentiment_words = StringField(required=True)
    accuracy = FloatField(required=True)
    user_desc = StringField(required=True)
    user_name = StringField(required=True)
    user_loc = StringField(required=True)
    geometry = PointField(required=True)

    meta = {
        'collection': 'twitter_data'  # Specify the collection name in MongoDB
    }

    @classmethod
    def save_db(cls, tenant_id, query_uuid, tag_filter, data_list):
        twitter_fields = [field_name for field_name, field in cls._fields.items()]

        try:
            for data in data_list:
                data = {key: value for key, value in data.items() if key in twitter_fields}
                twitter_data = cls(
                    tenant_id=tenant_id,
                    query_uuid=query_uuid,
                    tag_filter=tag_filter,
                    **data
                )
                twitter_data.save()
        except Exception as e:
            print(f"Error saving data to MongoDB: {e}")