import nltk
from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer

class OurStemmer():

    def __init__(self, custom_tokens):
        self.custom_tokens = custom_tokens
        self.stemmer = SnowballStemmer("italian")

    def stem(self, token):
        if token in self.custom_tokens:
            return token
        return self.stemmer.stem(token)

class DataPreprocesser():

    # TODO add readibility
    def __init__(self):
        nltk.download('stopwords')
        self.italian_punctuation = punctuation + "’"
        self.stopwords = set(stopwords.words('italian') + stopwords.words('english'))
        self.tokenizer = TweetTokenizer()
        # TODO how to read externally?
        self.stemmer = OurStemmer(open("words.txt", "r").read().split('\n'))
    
    def remove_emptytweets(self, data):
        return list(filter(lambda a: a != [], data))

    def is_stopword(self, word: str):
        return word in self.stopwords

    def is_punctuation(self, word: str):
        return word in self.italian_punctuation

    def tokenize_tweet(self, tweet: str):
        return [word for word in self.tokenizer.tokenize(tweet) if not self.is_punctuation(word) and not self.is_stopword(word)]

    def tokenize_data(self, data: dict):
        POLITICIANS = data.keys()
        return {politician: self.remove_emptytweets([self.tokenize_tweet(tweet) for tweet in data[politician]]) for politician in POLITICIANS}

    # fixme here tweet is a list? not a string?
    def stem_tweet(self, tweet: list):
        return [self.stemmer.stem(word) for word in tweet] 

    # fixme where to put POLITICIANS
    def stem_data(self, data: dict):
        POLITICIANS = data.keys()
        return {politician: self.remove_emptytweets([self.stem_tweet(tweet) for tweet in data[politician]]) for politician in POLITICIANS}

    def preprocess_data(self, data: dict, stem = True):
        tokenized_data = self.tokenize_data(data)
        return self.stem_data(tokenized_data) if stem else tokenized_data
