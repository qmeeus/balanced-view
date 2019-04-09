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

    languages = {
        'en': 'english',
        'nl': 'dutch',
        'de': 'german',
    }

    def __init__(self, text, language='en', **kwargs):
        self.input_text = self.process_input(text, method="remove")
        self.language = language

        # summa options
        self.min_results = kwargs.get("min_results", 3)
        self.max_results = kwargs.get("max_results", 5)
        self.min_score = kwargs.get("min_score", .05)

        # newsapi options
        self.default_period = kwargs.get("default_period", {"months": 1})
        self.source_file = kwargs.get("source_file", absolute_path("api_sources.json"))
        self.keyfile = kwargs.get("keyfile", absolute_path("apikey"))
        default_start_date = date.today() - relativedelta(**self.default_period)
        self.start_date = self.format_date(kwargs.get("start_date", default_start_date))
        self.end_date = self.format_date(kwargs.get("end_date", date.today()))

        # display options
        self.max_articles = kwargs.get("max_articles", 2)

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
        kwds, (graph, l2w, scores) = keywords(self.input_text, 
                                              language=self.languages[self.language], 
                                              ratio=1.0, 
                                              split=True, 
                                              scores=True)

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
        return {k: v[:self.max_articles] for k, v in sorted_sources.items()}

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


if __name__ == '__main__':
    from pprint import pprint

    texts = ["""
Everybody agrees that ObamaCare doesn’t work. Premiums & deductibles are far too high - Really bad HealthCare! Even the Dems want to replace it, but with Medicare for all, which would cause 180 million Americans to lose their beloved private health insurance. The Republicans are developing a really great HealthCare Plan with far lower premiums (cost) & deductibles than ObamaCare. In other words it will be far less expensive & much more usable than ObamaCare. Vote will be taken right after the
Election when Republicans hold the Senate & win back the House. It will be truly great HealthCare that will work for America. Also, Republicans will always support Pre-Existing Conditions. The Republican Party will be known as the Party of Great HealtCare. Meantime, the USA is doing better than ever & is respected again!""",

"""
The Democrats today killed a Bill that would have provided great relief to Farmers and yet more money to Puerto Rico despite the fact that Puerto Rico has already been scheduled to receive more hurricane relief funding than any “place” in history. The people of Puerto Rico are GREAT, but the politicians are incompetent or corrupt. Puerto Rico got far more money than Texas & Florida combined, yet their government can’t do anything right, the place is a mess - nothing works. FEMA & the Military
worked emergency miracles, but politicians like the crazed and incompetent Mayor of San Juan have done such a poor job  of bringing the Island back to health. 91 Billion Dollars to Puerto Rico, and now the Dems want to give them more, taking dollars away from our Farmers and so many others. Disgraceful!""",

"""
Mexico must use its very strong immigration laws to stop the many thousands of people trying to get into the USA. Our detention areas are maxed out & we will take no more illegals. Next step is to close the Border! This will also help us with stopping the Drug flow from Mexico!""",

"""
Stop & search is necessary to bring down knife crime. We need to be tough. We need to back our police. We need to change the odds in the minds of the kids who carry knives. And we can. We’ve done it before"""]

    for text in texts:
        fakenews = FakeNewsAPI(text)
        graph = fakenews.get_graph()
        pprint(graph)
        #results, (_, _, scores) = keywords(text)
        #print("\nOriginal text:")
        #pprint(text)
        #print("\nKeywords:")
        #print(results)
        #print("\nScores:")
        #pprint(sorted(scores.items(), key=lambda t: t[1], reverse=True))
        #print("\n" + "="*100)



    # articles = fakenews.get_results()
    # pprint(articles)
    # with open(absolute_path('results.json'), 'w') as f:
    #     json.dump(articles, f)
