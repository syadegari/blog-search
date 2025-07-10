import os
import json
import glob
import subprocess
import tqdm
import shutil


COLL_DIR  = "data/collection"          # Pyserini will read from here
INDEX_DIR = "data/indexes/bm25"

# 1) (Re)build clean collection dir
if os.path.exists(COLL_DIR):
    shutil.rmtree(COLL_DIR)
os.makedirs(COLL_DIR, exist_ok=True)

# 2) Convert our docs to Pyserini's JSON schema
for fp in tqdm.tqdm(glob.glob("data/json/*.json")):
    d = json.load(open(fp))
    out_fp = os.path.join(COLL_DIR, os.path.basename(fp))
    with open(out_fp, "w") as f:
        json.dump(
            {"id": d["id"], "contents": f"{d['title']} {d['body']}"},
            f,
            ensure_ascii=False,
        )

# 3) Call Pyserini to build a Lucene BM25 index
subprocess.run(
    [
        "python",
        "-m",
        "pyserini.index.lucene",
        "-collection",
        "JsonCollection",
        "-generator",
        "DefaultLuceneDocumentGenerator",
        "-threads",
        "4",
        "-input",
        COLL_DIR,
        "-index",
        INDEX_DIR,
        "-storePositions",
        "-storeDocvectors",
        "-storeRaw",
    ],
    check=True,
)
print(f"\n OK: Lucene BM25 index written to {INDEX_DIR}")
