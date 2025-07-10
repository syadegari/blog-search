import glob
import json
import faiss
import numpy as np
import tqdm
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vecs, ids = [], []

for fp in tqdm.tqdm(glob.glob("data/json/*.json")):
    doc = json.load(open(fp))
    vecs.append(model.encode(f"{doc['title']} {doc['body']}", normalize_embeddings=True))
    ids.append(doc["id"])

vecs = np.vstack(vecs).astype("float32")
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)
faiss.write_index(index, "data/indexes/faiss.index")
json.dump(ids, open("data/indexes/id_map.json", "w"))
