"""Step 3: retrieve the most relevant policy passages (TF-IDF cosine similarity)."""
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    def __init__(self, kb_path="data/knowledge_base.json"):
        self.docs = json.load(open(kb_path, encoding="utf-8"))
        self.vec = TfidfVectorizer(stop_words="english")
        self.matrix = self.vec.fit_transform([d["title"] + " " + d["text"] for d in self.docs])

    def search(self, query, k=2, min_score=0.05):
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        order = sims.argsort()[::-1][:k]
        return [{**self.docs[i], "score": float(sims[i])} for i in order if sims[i] >= min_score]
