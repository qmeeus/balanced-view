import pandas as pd
import numpy as np
import time

# from nltk import word_tokenize, pos_tag
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from utils.logger import logger

URL_RGX = r"((http|ftp|https):\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"


class Config:
    filename = "data/english.csv"
    nrows = 100

    count_vect = {}
    tfidf_vect = {"stop_words": "english"}


def main():
    config = Config()
    data = load_data(config.filename, config.nrows)
    data = preprocessing(data)
    model = build_model(config)
    train(model, data["tweet_text"])
    predictions = predict(model, data["tweet_text"].values[:10])
    logger.info(predictions)


def load_data(filename, nrows=None):
    t0 = time.time()

    def clean(df):
        df["tweet_time"] = pd.to_datetime(df["tweet_time"], format="%Y-%m-%d %H:%M")
        df["tweet_text"] = df["tweet_text"].str.replace(URL_RGX, "%URL%")
        return df.set_index('tweet_time')[["tweet_text"]]

    data = pd.read_csv(filename, nrows=nrows)
    data = clean(data)

    logger.info("Loaded {} rows x {} cols in {:.2f} s,".format(*data.shape, time.time() - t0))
    return data


def preprocessing(data):
    # def _preprocessing(text):
    #     return pos_tag(word_tokenize(text))

    # data["pos_tags"] = data["tweet_text"].map(preprocessing)
    return data

def build_model(config):
    # vectorizer = CountVectorizer(config.count_vect)
    vectorizer = TfidfVectorizer(**config.tfidf_vect)
    pipeline = Pipeline([("vect", vectorizer)])
    return pipeline


def train(model, data):
    t0 = time.time()
    model.fit(data)
    logger.info("Model trained in {:.2f} s.".format(time.time() - t0))
    return model


def predict(model, data, top=5):
    features = model.named_steps["vect"].get_feature_names()
    predictions = model.transform(data).tocoo()
    dense = list(zip(predictions.row, predictions.col, predictions.data))
    return (pd.DataFrame.from_records(dense, columns=["row", "column", "tfidf"])
            .sort_values(["row", "tfidf"], ascending=[True, False])
            .assign(features=lambda df: df["column"].map(lambda i: features[i]))
            .drop("column", axis=1)
            .set_index(["row", "features"])
            .groupby(level=0)
            .head(top))

# def download_nltk():
#     import nltk
#     nltk.download("punkt")
#     nltk.download("averaged_perceptron_tagger")


if __name__ == '__main__':
    main()
