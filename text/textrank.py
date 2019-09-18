import sys
import operator
from collections import defaultdict
from typing import List, Dict, Optional, Any, Union, Tuple

from text.utils.analyse import identify_language, load_model


class TextrankGraph:
    '''textrank graph'''
    def __init__(self,
                 damping_factor:Optional[float]=0.85, 
                 convergence_thresh:Optional[float]=1e-5, 
                 steps:Optional[int]=1000) -> None:

        self.graph = defaultdict(list)
        self.damping_factor = damping_factor
        self.convergence_thresh = convergence_thresh
        self.steps = steps

    def add_edge(self, start:str, end:str, weight:Union[int,float]) -> None:
        """Add edge between node"""
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    def to_json(self):
        nodes2index = {node: i for i, node in enumerate(self.graph)}
        return {
            "nodes": [
                {"name": node, "score": score}
                for node, score in self.rank().items()
            ],
            "links": [
                {"source": nodes2index[source], "target": nodes2index[target], "weight": weight} 
                for source, target, weight in self.graph.values()
            ]
        }

    def rank(self) -> Dict[str,float]:
        """Rank all nodes"""
        weight_default = 1.0 / (len(self.graph) or 1.0)     # initialize weight
        nodeweight_dict = defaultdict(float)                # store weight of node
        outsum_node_dict = defaultdict(float)               # store wegiht of out nodes
        for node, edges_from in self.graph.items():         # initilize nodes weight by edges
            # node: was
            # edges_from: [('was', 'prison', 1), ('was', 'wrong', 1), ('was', 'bad', 1)]
            nodeweight_dict[node] = weight_default
            outsum_node_dict[node] = sum((w for (_, _, w) in edges_from), 0.0) # if no out edge, set weight 0
        
        sorted_keys = sorted(self.graph)                    # save node name as a list for iteration
        step, step_dict = 0, [0]
        while step < self.steps:
            step += 1
            for node, edges_from in self.graph.items():
                score = sum(
                    weight * nodeweight_dict[cword] / outsum_node_dict[cword] 
                    for (word, cword, weight) in edges_from
                )
                
                nodeweight_dict[node] = (1 - self.damping_factor) + self.damping_factor * score

            step_dict.append(sum(nodeweight_dict.values()))

            if abs(step_dict[step] - step_dict[step - 1]) <= self.convergence_thresh:
                break

        # min-max scale to make result in range to [0 - 1]
        weights = list(nodeweight_dict.values())
        min_rank, max_rank = min(weights), max(weights)
        for node, weight in nodeweight_dict.items():
            # min_rank = min_rank / 10
            nodeweight_dict[node] = (weight - min_rank) / (max_rank - min_rank)

        return nodeweight_dict


class TextRank:
    """Extract keywords based on textrank graph algorithm"""

    DEFAULT_INCLUDE_POS = ['NOUN', 'PROPN', 'VERB']
    DEFAULT_EXCLUDE_POS = ['NUM', 'ADV']

    def __init__(self, 
                 lang:Optional[str]=None,
                 candidate_pos:Optional[List[str]]=None, 
                 filter_pos:Optional[List[str]]=None, 
                 min_length:Optional[int]=1, 
                 span:Optional[int]=5) -> None:

        self.lang = lang
        self.candi_pos = candidate_pos or self.DEFAULT_INCLUDE_POS
        self.stop_pos = filter_pos or self.DEFAULT_EXCLUDE_POS
        self.min_length = min_length
        self.span = span

    def analyse_text(self, text:str) -> List[Tuple[str,str]]:
        if not self.lang:
            self.lang = identify_language(text)
        model = load_model(self.lang)
        document = model(text)

        tokens = map(operator.attrgetter('text'), document)
        pos_tags = map(operator.attrgetter('pos_'), document)
        # dependencies = map(operator.attrgetter('dep_'), document)
        # iob_labels = map(operator.attrgetter('ent_iob_'), document)
        # entity_labels = map(operator.attrgetter('ent_type_'), document)
        return list(zip(tokens, pos_tags)) #, dependencies, iob_labels, entity_labels))

    def extract_keywords(self, text:str, num_keywords:int) -> List[Tuple[str,float]]:

        self.g_ = TextrankGraph()
        wordlist = self.analyse_text(text)
        cm = defaultdict(int)
        for i, (word, pos) in enumerate(wordlist):
            if pos in self.candi_pos and len(word) > self.min_length:
                for j, (cword, cpos) in enumerate(wordlist[i + 1:i + self.span + 1]):
                    if cpos in self.candi_pos and len(cword) > self.min_length:
                        cm[(word, cword)] +=  1

        # cm = {('was', 'prison'): 1, ('become', 'prison'): 1}
        for (word, cword), weight in cm.items():
            self.g_.add_edge(word, cword, weight)

        nodes_rank = self.g_.rank()
        nodes_rank = sorted(nodes_rank.items(), key=operator.itemgetter(1), reverse=True)

        return nodes_rank[:num_keywords]
