from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize model globally so it's only loaded once per worker/process
# This will download the ~80MB model automatically on first run
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading local embedding model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model

def classify_chunks_batch(chunk_texts, syllabus_topics, threshold=0.3):
    """
    Classifies a batch of text chunks into syllabus topics using local embeddings.
    
    Args:
        chunk_texts (list of str): The text contents of the chunks.
        syllabus_topics (list of str): List of possible topic names.
        threshold (float): Minimum cosine similarity to assign a topic.
        
    Returns:
        list of str: The name of the best matching topic for each chunk, or "Uncategorized".
    """
    if not chunk_texts or not syllabus_topics:
        return ["Uncategorized"] * len(chunk_texts)
        
    model = get_model()
    
    print(f"Embedding {len(chunk_texts)} chunks and {len(syllabus_topics)} topics...")
    chunk_embeddings = model.encode(chunk_texts)
    topic_embeddings = model.encode(syllabus_topics)
    
    print("Computing similarity...")
    similarities = cosine_similarity(chunk_embeddings, topic_embeddings)
    
    results = []
    for sim_array in similarities:
        best_idx = np.argmax(sim_array)
        best_score = sim_array[best_idx]
        if best_score >= threshold:
            results.append(syllabus_topics[best_idx])
        else:
            results.append("Uncategorized")
            
    return results
