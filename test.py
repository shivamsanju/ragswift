from sentence_transformers import SentenceTransformer
sentences = ["Hello", "Hi", "Fuck you"]
model = SentenceTransformer('BAAI/bge-base-en-v1.5')
embeddings = model.encode(sentences, normalize_embeddings=True)
scores = []
query_emb = embeddings[0]
for em in embeddings[1:]:
    similarity = query_emb @ em
    scores.append(similarity)
print(scores)
