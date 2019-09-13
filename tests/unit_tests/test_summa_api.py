import pandas as pd
from summa.graph import Graph
from api.clients import Summary
from tests.utils import load_test_data


def test_summa():
    for text in load_test_data():
        try:
            _test_summa(text)
        except ValueError as e:
            if "No keyword found" in str(e):
                print(f"No keyword found for: {text}")
            else:
                raise e

def _test_summa(text):
    
    summary = Summary().fit(text)

    attributes = ("keywords_", "graph_", "lemma2words_", "scores_")

    assert all(hasattr(summary, attr) for attr in attributes)
    
    kwds, graph, l2w, scores = (getattr(summary, attr) for attr in attributes)
    assert isinstance(kwds, pd.DataFrame) and len(kwds)
    assert isinstance(graph, Graph) and graph.nodes() and graph.edges()
    assert isinstance(l2w, dict) and l2w
    assert isinstance(scores, dict) and scores
    print(f"Ignored: {[token for token in l2w if token not in scores]}")

    max_kws = 5
    k2k = summary._keywords_to_keep(max_kws)
    assert type(k2k) is list and len(k2k) <= max_kws

    kwds = summary.get_keywords()
    assert type(kwds) is list

    graph = summary.get_graph()
    assert type(graph) is dict and graph
    nodes, edges = (graph.pop(key) for key in ("nodes", "links"))
    assert not(graph)
    assert type(nodes) is list and nodes
    assert type(edges) is list and edges
    assert all(type(node) is dict for node in nodes)
    assert all(type(edge) is dict for edge in edges)

    print(f"Keywords: {kwds}")
    print(f"Graph: {len(nodes)} nodes and {len(edges)} edges")


if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    test_summa()
