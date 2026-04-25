import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

def retrieve_chunks(topic_tag, k=5):
    """
    Given a topic, embeds the topic and retrieves the top-K 
    most relevant chunks from ChromaDB using local embeddings.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vectorstore = Chroma(
        collection_name="student_helper_rag",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    
    # Use Chroma to retrieve chunks. We filter by Topic_Tag 
    # to only get chunks relevant to the current subject.
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"Topic_Tag": topic_tag}
        }
    )
    
    # Retrieve documents using the topic as the query 
    # (since the user searches for the topic to get tested)
    results = retriever.invoke(topic_tag)
    
    return results
