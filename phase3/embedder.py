import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

def embed_and_store(documents):
    """
    Takes LangChain Documents, embeds them using Gemini, 
    and stores them persistently in ChromaDB.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("GEMINI_API_KEY is missing or invalid in the .env file")
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
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
