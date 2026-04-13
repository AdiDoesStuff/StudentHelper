from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_text(pages_data, topic_tag):
    """
    Splits text from pages into roughly 500-word chunks (approx 2000 chars)
    with a small overlap, tagging each chunk with the topic_tag and page number.
    Returns a list of Langchain Document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=250,
        separators=["\n\n", "\n", " ", ""]
    )
    
    documents = []
    
    for page in pages_data:
        text = page.get("text", "")
        if not text.strip():
            continue
            
        # Split text into smaller chunks
        chunks = splitter.split_text(text)
        
        for chunk in chunks:
            # Create a Langchain Document
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": page.get("page"),
                    "Topic_Tag": topic_tag
                }
            )
            documents.append(doc)
            
    return documents
