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

    def __init__(self):
        nltk.download('stopwords')
        self.italian_punctuation = punctuation + "’"
        self.stopwords = set(stopwords.words('italian') + stopwords.words('english'))
        self.tokenizer = TweetTokenizer()
        # TODO how to read externally?
        self.stemmer = OurStemmer(open("custom_tokens.txt", "r").read().split('\n'))

    def is_stopword(self, word: str):
        return word in self.stopwords

    def is_punctuation(self, word: str):
        return word in self.italian_punctuation

    def tokenize_tweet(self, tweet: str):
        return [word for word in self.tokenizer.tokenize(tweet) if not self.is_punctuation(word) and not self.is_stopword(word)]

    def tokenize_data(self, data):
        tokenized_data = data.copy()
        tokenized_data["original_text"] = data["text"]
        tokenized_data["text"] = data["text"].map(lambda text: self.tokenize_tweet(text))
        return tokenized_data

    def stem_tweet(self, tweet: list):
        return [self.stemmer.stem(word) for word in tweet] 

    def stem_data(self, data):
        stemmed_data = data.copy()
        stemmed_data["text"] = data["text"].map(lambda text: self.stem_tweet(text))
        # Drop empty and duplicated tweets
        unique_stemmed_data = stemmed_data.loc[stemmed_data.astype(str).drop_duplicates("text").index]
        return unique_stemmed_data[unique_stemmed_data["text"].astype(str) != "[]"]

    def preprocess_data(self, data, stem = True):
        tokenized_data = self.tokenize_data(data)
        return self.stem_data(tokenized_data) if stem else tokenized_data