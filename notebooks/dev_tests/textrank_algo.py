import numpy as np


def textrank_algorithm(G, d=0.8):

    k = len(G)
    outgoing = G.sum(0)
    scores = np.ones((k,)) * 1/k

    sse = lambda x, y: ((x - y)**2).sum()

    for step in range(10):

        newscores = np.empty((k,))
        for j in range(k):
            newscores[j] = d / k + (1-d) * np.sum([
                scores[l] / outgoing[l] 
                for l in range(k) 
                if l != j and G[j,l] != 0
            ])

        print(f"{step} SSE:{sse(scores, newscores):.2e}, {newscores}")
        scores = newscores

    return scores


if __name__ == '__main__':
    G = np.array([
        [0,0,0,0],
        [0,0,0,0],
        [1,0,0,0],
        [0,0,0,0]
    ])

    d = 0.8

    print(textrank_algorithm(G, d))
