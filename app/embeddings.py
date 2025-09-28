from sentence_transformers import SentenceTransformer

# load once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    return model.encode(text).tolist()

