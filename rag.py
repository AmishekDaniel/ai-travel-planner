import os
import numpy as np
import faiss
from groq import Groq
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_chunks(text, source, chunk_size=200):
    return [{"text": text[i:i + chunk_size], "source": source}
            for i in range(0, len(text), chunk_size)]


def load_folder(folder_path):
    chunks = []
    for name in os.listdir(folder_path):
        with open(os.path.join(folder_path, name), "r", encoding="utf-8") as f:
            chunks.extend(load_chunks(f.read(), name))
    return chunks


class Planner:
    """Loads the model and builds the search index ONCE."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it in Space Settings -> Secrets.")
        self.client = Groq(api_key=api_key)
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = load_folder(DATA_DIR)
        vectors = self.embed_model.encode([c["text"] for c in self.chunks])
        self.index = faiss.IndexFlatL2(vectors.shape[1])
        self.index.add(np.array(vectors, dtype="float32"))

    def search(self, query, top_k=4):
        q = self.embed_model.encode([query]).astype("float32")
        _, ids = self.index.search(q, top_k)
        return [self.chunks[i] for i in ids[0] if i != -1]

    def answer(self, query):
        context = "".join(f"{c['text']}\n{c['source']}\n\n" for c in self.search(query))
        prompt = f""" Give the answer only.
    Answer only from the following context
    context: {context}
    input: {query}
    """
        res = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
