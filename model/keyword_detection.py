import os.path as p
import pandas as pd
import numpy as np
import time
import pickle

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

try:
    from .utils.logger import logger
except ImportError:
    from utils.logger import logger

URL_RGX = r"((http|ftp|https):\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"


class Config:

    filename = p.join(p.dirname(p.abspath(__file__)), "data/english.csv")
    model_file = p.join(p.dirname(p.abspath(__file__)), "outputs/model.pkl")
    nrows = 10000
    count_vect = {}
    tfidf_vect = {
        "strip_accents": "ascii",
        "stop_words": "english",
    }


class Model:

    def __init__(self, config, load_from_file=False):
        self.config = config
        self.pipeline = None
        if load_from_file:
            self.pipeline = self.load()
            self.is_trained = True
        else:
            self.build_model()
            self.is_trained = False

    def build_model(self):
        # vectorizer = CountVectorizer(config.count_vect)
        vectorizer = TfidfVectorizer(**self.config.tfidf_vect)
        pipeline = Pipeline([("vect", vectorizer)])
        self.pipeline = pipeline

    def train(self, data):
        t0 = time.time()
        self.pipeline.fit(data)
        logger.info("Model trained in {:.2f} s.".format(time.time() - t0))
        self.is_trained = True

    def predict(self, data, top=5):
        model = self.pipeline
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

    def save(self):
        with open(self.config.model_file, "wb") as f:
            pickle.dump(self.pipeline, f)

    def load(self):
        with open(self.config.model_file, "rb") as f:
            return pickle.load(f)


class Data:
    def __init__(self, config):
        t0 = time.time()

        def clean(df):
            df["tweet_time"] = pd.to_datetime(df["tweet_time"], format="%Y-%m-%d %H:%M")
            df["tweet_text"] = df["tweet_text"].str.replace(URL_RGX, "%URL%")
            return df.set_index('tweet_time')[["tweet_text"]]

        data = pd.read_csv(config.filename, nrows=config.nrows)
        data = clean(data)

        logger.info("Loaded {} rows x {} cols in {:.2f} s,".format(*data.shape, time.time() - t0))
        self.values = data

    def preprocess(self):
        data = self.values
        # def _preprocessing(text):
        #     return pos_tag(word_tokenize(text))

        # data["pos_tags"] = data["tweet_text"].map(preprocessing)
        self.values = data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Trainer for keyword detection")
    parser.add_argument("--save", action="store_true", default=False, help="Save model")
    parser.add_argument("--predict", action="store_true", default=False, help="Test model")
    parser.add_argument("--n_predictions", type=int, default=2, help="Number of examples to test on")
    args = parser.parse_args()

    config = Config()
    model = Model(config)
    data = Data(config)
    model.train(data.values["tweet_text"])
    if args.save:
        model.save()
    if args.predict:
        predictions = model.predict(np.random.choice(data.values["tweet_text"].values, args.n_predictions))
        logger.info(predictions)

