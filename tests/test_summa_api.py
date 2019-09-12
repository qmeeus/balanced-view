from api.clients import Summary

text = """
    Everybody agrees that ObamaCare doesn’t work. Premiums & deductibles are far too high - Really bad HealthCare! Even the Dems want to replace it, but with Medicare for all, which would cause 180 million Americans to lose their beloved private health insurance. The Republicans are developing a really great HealthCare Plan with far lower premiums (cost) & deductibles than ObamaCare. In other words it will be far less expensive & much more usable than ObamaCare. Vote will be taken right after the
    Election when Republicans hold the Senate & win back the House. It will be truly great HealthCare that will work for America. Also, Republicans will always support Pre-Existing Conditions. The Republican Party will be known as the Party of Great HealtCare. Meantime, the USA is doing better than ever & is respected again!
"""

summary = Summary(text)
print(summary.keywords)
print(summary.get_keywords())
graph = summary.get_graph()
nodes, edges = graph["nodes"], graph["links"]
print("Graph:", "{} nodes, {} edges".format(len(nodes), len(edges)))