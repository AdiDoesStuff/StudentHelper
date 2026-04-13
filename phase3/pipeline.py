import os
import sys

# Ensure parent directory is in sys.path so 'phase3...' imports work when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from phase3.ocr_extractor import extract_text
from phase3.chunker import chunk_text
from phase3.embedder import embed_and_store
from phase3.rag_engine import retrieve_chunks
from phase3.question_generator import generate_questions

def run_pipeline(pdf_path, topic_tag, generate_count=5):
    print(f"--- Starting Pipeline for PDF: {pdf_path} | Topic: {topic_tag} ---")
    
    print("1. Extracting text from PDF...")
    pages = extract_text(pdf_path)
    print(f"   -> Extracted {len(pages)} pages.")
    
    print("2. Chunking text...")
    chunks = chunk_text(pages, topic_tag)
    print(f"   -> Created {len(chunks)} chunks.")
    
    print("3. Embedding and storing chunks into ChromaDB...")
    embed_and_store(chunks)
    print("   -> Stored in ChromaDB.")
    
    print(f"4. Retrieving relevant context for '{topic_tag}'...")
    results = retrieve_chunks(topic_tag)
    print(f"   -> Retrieved {len(results)} relevant chunks.")
    
    print("5. Generating questions...")
    questions = generate_questions(results, num_questions=generate_count)
    print(f"   -> Generated {len(questions)} structured questions.")
    
    return questions
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pipeline.py <pdf_path> <topic_tag>")
        sys.exit(1)
        

    pdf_path = sys.argv[1]
    topic_tag = sys.argv[2]
    
    try:
        result = run_pipeline(pdf_path, topic_tag)
        print("\\n=== FINAL RESULT ===")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\\nPipeline Error: {e}")
