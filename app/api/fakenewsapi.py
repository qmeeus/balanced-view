import os
import re
import json
import pandas as pd
from summa.keywords import keywords

from newsapi import NewsApiClient
from datetime import date
from dateutil.relativedelta import relativedelta


def absolute_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class FakeNewsAPI:

    def __init__(self, text, language='en', **kwargs):
        self.input_text = self.process_input(text, method="remove")
        self.language = language

        # summa options
        self.min_results = kwargs.get("min_results", 2)
        self.max_results = kwargs.get("min_results", 3)
        self.min_score = kwargs.get("min_score", .2)

        # newsapi options
        self.default_period = kwargs.get("default_period", {"months": 1})
        self.source_file = kwargs.get("source_file", absolute_path("api_sources.json"))
        self.keyfile = kwargs.get("keyfile", absolute_path("apikey"))
        default_start_date = date.today() - relativedelta(**self.default_period)
        self.start_date = self.format_date(kwargs.get("start_date", default_start_date))
        self.end_date = self.format_date(kwargs.get("end_date", date.today()))

        # operations
        self.sources = self.load_sources()
        self.keywords, self.graph, self.l2w, self.scores = self.get_keywords()
        print("Keywords: {}".format(self.filter_keywords()))
        self.articles = self.fetch_articles()

    def get_results(self):
        if self.articles == "no-keywords-error":
            return {"error": {
                "text": "Keyword extraction failed!",
                "reason": "One frequent explanation is that the text is too short."}}
        if self.articles == "api-error":
            return {"error": {
                "text": "API error!",
                "reason": "It is possible that the api key was not found or is expired or we have reached our limit."}}
        if not self.articles["totalResults"]:
            return {"error": {
                "text": "Search yielded no results!",
                "reason": "We could not find related articles in any of the sources."}}
        return self.sort_articles()

    def fetch_articles(self):
        newsapi = NewsApiClient(api_key=self.load_key())
        filtered_kwds = self.filter_keywords()
        if filtered_kwds:
            try:
                return newsapi.get_everything(
                    q=filtered_kwds,
                    sources=self.filter_sources(),
                    from_param=self.start_date,
                    to=self.end_date,
                    language=self.language,
                    sort_by='relevancy')
            except Exception as e:
                print(e)
                return "api-error"
        else:
            return "no-keywords-error"

    def get_graph(self):

        if len(self.keywords) == 0:
            raise Exception("No keywords were extracted")

        nodes, edges = self.graph.nodes(), []
        for node_a, node_b in self.graph.edges():
            if (node_b, node_a) not in edges and node_a != node_b:
                edges.append((node_a, node_b))

        return {
            "nodes": list(map(self.get_node_info, nodes)),
            "links": [
                {"source": nodes.index(node_a), "target": nodes.index(node_b)} 
                for node_a, node_b in edges]
        }

    def get_node_info(self, node):
        name = self.l2w[node][0]
        print(name)
        score = self.scores[node]
        print(score)
        return {"name": name, "token": node, "score": score}

    def get_keywords(self):
        kwds, (graph, l2w, scores) = keywords(self.input_text, ratio=1.0, split=True, scores=True)
        return (
            pd.DataFrame(kwds, columns=["keyword", "score"]).sort_values("score", ascending=False), 
            graph, l2w, scores)

    def filter_keywords(self):
        try:
            to_keep = max(
                min((self.keywords["score"] > self.min_score).sum(), self.min_results), 
                self.max_results)
            return " ".join(self.keywords["keyword"].head(to_keep).values)
        except IndexError:
            return ""

    def sort_articles(self):
        source_map = {
            source: key 
            for key, sources in self.sources.items() 
            for source in sources}

        sorted_sources = {key: [] for key in self.sources.keys()}
        for article in self.articles["articles"]:
            if article["source"]["id"] in source_map:
                sorted_sources[source_map[article["source"]["id"]]].append(article)
        return sorted_sources

    def load_sources(self):
        with open(self.source_file) as f:
            sources = json.load(f)
        return {source_group["name"]: source_group["sources"] for source_group in sources}
    
    def filter_sources(self, influence="all"):
        sources = self.sources
        if influence == "all":
            sources_list = [s for l in sources.values() for s in l]
        else:
            assert influence in sources.keys(), "{} not in available political leanings".format(influence)
            sources_list = sources[influence]
        return ",".join(sources_list)

    def load_key(self):
        with open(self.keyfile) as f:
            return f.read().strip()

    @classmethod
    def process_input(cls, text, method="remove"):
        assert method in ["remove", "transform"]
        if method == "remove":
            return " ".join(filter(lambda s: not cls.flag_word(s), text.split()))
        else:
            return " ".join(map(cls.transform_hashtag, text.split()))

    @staticmethod
    def flag_word(word):
        # Flag mentions and hashtags
        return word[0] in ["#", "@"]

    @staticmethod
    def transform_hashtag(word):
        if word.startswith("#"):
            words = []
            for char in word[1:]:
                if char.isupper():
                    words.append([])
                words[-1].append(char)
            return " ".join(map("".join, words))
        return word

    @staticmethod
    def format_date(dt):
        return dt.strftime('%Y-%m-%d')


if __name__ == "__main__":
    from pprint import pprint
    # Test API
    text = """Democrat Stacey Abrams acknowledges that Republican Brian Kemp will be certified as 
    the next Georgia governor, but says she is not offering a speech of concession because that 
    would suggest the election process was just: "The state failed its voters" - @MSNBC"""
    fakenews = FakeNewsAPI(text)
    # articles = fakenews.get_results()
    # pprint(articles)
    graph = fakenews.get_graph()
    pprint(graph)
    # with open(absolute_path('results.json'), 'w') as f:
    #     json.dump(articles, f)
