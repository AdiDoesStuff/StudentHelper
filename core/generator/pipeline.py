import os
import sys

# Ensure root directory is in sys.path so 'core...' imports work when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from core.generator.ocr_extractor import extract_text
from core.generator.chunker import chunk_text
from core.generator.embedder import embed_and_store
from core.generator.rag_engine import retrieve_chunks
from core.generator.question_generator import generate_questions
from core.generator.classifier import classify_chunks_batch
import sqlite3

def get_topics_for_subject(subject_name):
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Topic_Name FROM Syllabus_Topics WHERE Subject_Name = ?", (subject_name,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def process_and_store_documents(pdf_paths, subject_name):
    print(f"--- Processing {len(pdf_paths)} PDFs for Subject: {subject_name} ---")
    
    syllabus_topics = get_topics_for_subject(subject_name)
    if not syllabus_topics:
        raise ValueError(f"No syllabus topics found for subject: {subject_name}")
        
    all_chunks = []
    
    # 1. Extract and chunk all PDFs
    for pdf_path in pdf_paths:
        print(f"Extracting text from: {pdf_path}")
        pages = extract_text(pdf_path)
        chunks = chunk_text(pages)
        all_chunks.extend(chunks)
        
    print(f"Total chunks extracted: {len(all_chunks)}")
    
    # 2. Classify chunks using local model
    chunk_texts = [doc.page_content for doc in all_chunks]
    assigned_topics = classify_chunks_batch(chunk_texts, syllabus_topics, threshold=0.3)
    
    # 3. Update metadata
    for i, doc in enumerate(all_chunks):
        doc.metadata["Subject_Name"] = subject_name
        doc.metadata["Topic_Tag"] = assigned_topics[i]
        
    # 4. Store in ChromaDB (uses Gemini embedding for storage so RAG still works)
    print("Embedding and storing classified chunks into ChromaDB...")
    embed_and_store(all_chunks)
    
    # Return summary
    summary = {}
    for topic in assigned_topics:
        summary[topic] = summary.get(topic, 0) + 1
        
    return summary

def run_pipeline(pdf_path, topic_tag, generate_count=5):
    print(f"--- Starting Pipeline for PDF: {pdf_path} | Topic: {topic_tag} ---")
    
    print("1. Extracting text from PDF...")
    pages = extract_text(pdf_path)
    print(f"   -> Extracted {len(pages)} pages.")
    
    print("2. Chunking text...")
    chunks = chunk_text(pages)
    
    # For legacy single-topic run_pipeline, manually assign the passed topic tag
    for doc in chunks:
        doc.metadata["Topic_Tag"] = topic_tag
        
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
