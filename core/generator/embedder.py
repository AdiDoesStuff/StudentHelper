import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

def embed_and_store(documents):
    """
    Takes LangChain Documents, embeds them using a local model, 
    and stores them persistently in ChromaDB.
    """
    # Using the same local model we use for classification!
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Initialize/connect to Chroma persistent storage
    vectorstore = Chroma(
        collection_name="student_helper_rag",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    
    # Store the documents
    if documents:
        vectorstore.add_documents(documents)
    
    return vectorstore
