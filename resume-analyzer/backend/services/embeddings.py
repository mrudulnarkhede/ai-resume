from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Load the embedding model
# ---------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# ---------------------------------------------------------
# Generate embeddings
# ---------------------------------------------------------

def generate_embedding(text):
    """
    Convert a piece of text into a numerical vector.
    """

    if not text or not text.strip():
        return None

    embedding = model.encode(text)

    return embedding


# ---------------------------------------------------------
# Generate embeddings for multiple texts
# ---------------------------------------------------------

def generate_embeddings(texts):
    """
    Convert multiple text strings into numerical vectors.
    """

    if not texts:
        return []

    embeddings = model.encode(texts)

    return embeddings


# ---------------------------------------------------------
# Test the embedding model
# ---------------------------------------------------------

if __name__ == "__main__":

    text = "Developed REST APIs using Python and Flask."

    embedding = generate_embedding(text)

    print("Text:")
    print(text)

    print("\nEmbedding generated successfully!")

    print("Vector dimensions:")
    print(len(embedding))

    print("\nFirst 10 values:")
    print(embedding[:10])