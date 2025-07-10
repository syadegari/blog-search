import json
import faiss
import numpy as np
from pyserini.search.lucene import LuceneSearcher as SimpleSearcher
from sentence_transformers import SentenceTransformer


BM25 = SimpleSearcher("data/indexes/bm25")
BM25.set_bm25(0.9, 0.4)  # TODO: should be tweaked later
Dense = faiss.read_index("data/indexes/faiss.index")
IDS   = json.load(open("data/indexes/id_map.json"))
Embed = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def rrf(ranks, k=60):
    """Reciprocal rank fusion given list of rank dicts"""
    scores = {}
    for rank in ranks:
        for r, doc_id in enumerate(rank):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + r + 1)
    return scores


def search(query, topk=10):
    # sparse results
    hits = BM25.search(query, 50)  # TODO: should this be parametrized? 
    sparse_ids = [h.docid for h in hits]

    # dense results
    qvec = Embed.encode(query, normalize_embeddings=True)
    _,I  = Dense.search(np.array([qvec]).astype("float32"), 50)
    dense_ids = [IDS[i] for i in I[0]]

    fused_scores = rrf([sparse_ids, dense_ids])
    # sort by score DESC
    ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:topk]
    return [{"url": doc_id, "score": round(score, 4)} for doc_id, score in ranked]

if __name__=="__main__":
    print(search("product–market fit memo"))
