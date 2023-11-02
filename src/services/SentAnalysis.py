import re
import string

from nltk import FreqDist
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from sentimentr import sentimentr

SID = SentimentIntensityAnalyzer()
LABELS_SENTIMENTS = {0: "very negative", 1: "negative", 2: "neutral", 3: "positive", 4: "very positive"}
FILTER_FIELDS = ['conversation_id', 'created_at', 'id', 'text', 'author_id', 'x', 'y', 'sentiment',
                 'sentiment_score', 'neg_score', 'neu_score', 'pos_score', 'neg_sent_words', 'pos_sent_words',
                 'neu_sent_words', 'neg_words_count', 'pos_words_count', 'neu_words_count']


class SentAnalysis(object):

    def __init__(self):
        self._download_nltk_resources()

    def _download_nltk_resources(self):
        # wordnet is a lexical database for the English language that helps the script determine the base word.
        # You need the averaged_perceptron_tagger resource to determine the context of a word in a sentence.

        # punkt borrar
        resources = ["wordnet", "punkt", "stopwords", "averaged_perceptron_tagger"]

        for resource in resources:
            try:
                nltk.data.find(f"tokenizers/{resource}")
            except LookupError:
                nltk.download(resource)

    # clean tokens that does not add meaning or information to data
    def _remove_noise(self, tweet_tokens, stop_words=()):
        cleaned_tokens = []
        # normalizes a sentence, convert words with the same meaning but different forms.
        # you should first generate the tags for each token in the text,
        # and then lemmatize each word using the tag.
        for token, tag in pos_tag(tweet_tokens):
            # remove Hyperlinks
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                           '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
            # remove Twitter handles in replies
            token = re.sub("(@[A-Za-z0-9_]+)", "", token)

            token = token.strip()

            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            # legitimization algorithm analyzes the structure of the word and its context to convert it to a
            # normalized form, according to the context for each word in your text using a tagging algorithm,
            # which assesses the relative position of a word in a sentence, thanks to wordnet is a lexical database
            # for the English language and averaged_perceptron_tagger that provides a list of tokens.
            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            # remove all punctuation and special characters from tweets and the most common words
            # in a language are called stop words.
            if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())
        return cleaned_tokens

    # function that cleans the sentence thought tokenizing, normalizing and cleaning noise from the data
    def _clean_sentence(self, sentence):
        # pre-cleaning data
        sentence = sentimentr.remove_punctuation(sentence)
        # tokenizing a single tweet (refers to the process of breaking down text data into individual words or phrases,
        # known as tokens. This is often done to analyze, manipulate, or process text data in smaller chunks)
        tokens = sentimentr.word_tokenize(str(sentence).lower())
        # method to get a list of stop words in English to remove
        stop_words = stopwords.words('english')
        tokens_clean = self._remove_noise(tokens, stop_words)
        return tokens_clean

    # extent sentiment polarity labels according to score
    def _get_label_class(self, score):
        label = None
        if score >= 0.7:
            label = LABELS_SENTIMENTS[4]
        elif score >= 0.2:
            label = LABELS_SENTIMENTS[3]
        elif score >= -0.2:
            label = LABELS_SENTIMENTS[2]
        elif score >= -0.7:
            label = LABELS_SENTIMENTS[1]
        else:
            label = LABELS_SENTIMENTS[0]

        return label

    # get sentiment words and count classification
    def _sentiment_classification(self, clean_tokens):
        pos_word_list = []
        neu_word_list = []
        neg_word_list = []
        for word in clean_tokens:
            score = SID.polarity_scores(word)['compound']
            if score >= 0.3:
                pos_word_list.append(word)
            elif score >= -0.3:
                neu_word_list.append(word)
            else:
                neg_word_list.append(word)

        return {
            'neg_sent_words': ','.join([str(elem) for elem in neg_word_list]),
            'pos_sent_words': ','.join([str(elem) for elem in pos_word_list]),
            'neu_sent_words': ','.join([str(elem) for elem in neu_word_list]),
            'neg_words_count': len(neg_word_list),
            'pos_words_count': len(pos_word_list),
            'neu_words_count': len(neu_word_list),
            'most_neg_word': FreqDist(neg_word_list).most_common(1)[0][0] if neg_word_list else '',
            'most_pos_word': FreqDist(pos_word_list).most_common(1)[0][0] if pos_word_list else '',
            'most_neu_word': FreqDist(neu_word_list).most_common(1)[0][0] if neu_word_list else ''
        }

        # get sentiment words and count classification

    def _sentiment_data(self, data, sentiment):
        if 'positive' in sentiment:
            return {'sentiment_word': data.get('most_pos_word', None),
                    'sentiment_words': data.get('pos_sent_words', None)}
        elif 'negative' in sentiment:
            return {'sentiment_word': data.get('most_neg_word', None),
                    'sentiment_words': data.get('neg_sent_words', None)}
        else:
            return {'sentiment_word': data.get('most_neu_word', None),
                    'sentiment_words': data.get('neu_sent_words', None)}

    # get sentiment score and classification
    def sentiment_fit(self, data, text_column):
        sentence = data.get(text_column)
        tokens_clean = self._clean_sentence(sentence)
        # it takes in a string as input and returns a dictionary containing the polarity scores of the text
        # in different emotional categories, such as positive, negative, and neutral.
        sentence_clean = ' '.join([str(elem) for elem in tokens_clean])
        score = round(SID.polarity_scores(sentence_clean)['compound'], 2)
        data['sentiment'] = self._get_label_class(score)
        data['sentiment_score'] = score
        data['neg_score'] = round(SID.polarity_scores(sentence_clean)['neg'], 2)
        data['neu_score'] = round(SID.polarity_scores(sentence_clean)['neu'], 2)
        data['pos_score'] = round(SID.polarity_scores(sentence_clean)['pos'], 2)
        sentiment_class = self._sentiment_classification(tokens_clean)
        extra_sentiment = self._sentiment_data(sentiment_class, data['sentiment'])
        data['text'] = sentence_clean
        data = {**data, **sentiment_class, **extra_sentiment}
        return data
