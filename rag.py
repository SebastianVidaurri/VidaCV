import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAG:

    def __init__(self, knowledge_path="knowledge"):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.texts = []
        self.load_knowledge(knowledge_path)

        print("Chunks cargados:", len(self.texts)) # Imprimimos la cantidad de chunks cargados para verificar que se cargaron correctamente

        self.embeddings = self.model.encode(self.texts)

        dimension = self.embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(self.embeddings))

    def load_knowledge(self, path):

        for file in os.listdir(path):

            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                text = f.read()

                chunks = []
                current_chunk = ""

                for line in text.split("\n"):
                    if len(current_chunk) + len(line) < 500:
                        current_chunk += " " + line
                    else:
                        chunks.append(current_chunk.strip())
                        current_chunk = line

                if current_chunk:
                    chunks.append(current_chunk.strip())

                for chunk in chunks:
                    if chunk.strip():
                        self.texts.append(chunk)

    def search(self, query, k=3):

        query_embedding = self.model.encode([query])

        distances, indices = self.index.search(
            np.array(query_embedding), k
        )

        results = []

        for idx in indices[0]:
            results.append(self.texts[idx])

        return results