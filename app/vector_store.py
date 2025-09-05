import chromadb
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from  langchain_community.vectorstores import Chroma
from typing import List, Dict
import hashlib

from app.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def create_collection_for_client(self, client_id: str):
        """Create a collection for a specific client"""
        collection_name = f"client_{client_id}"
        try:
            collection = self.client.get_collection(collection_name)
        except:
            collection = self.client.create_collection(collection_name)
        return collection
    
    def add_knowledge(self, client_id: str, content: str, source: str = None) -> List[str]:
        """Add knowledge to client's vector store"""
        collection = self.create_collection_for_client(client_id)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Generate embeddings and add to collection
        document_ids = []
        for i, chunk in enumerate(chunks):
            doc_id = f"{client_id}_{source or 'unknown'}_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"
            
            # Get embedding
            embedding = self.embeddings.embed_query(chunk)
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"client_id": client_id, "source": source or "unknown"}],
                ids=[doc_id]
            )
            document_ids.append(doc_id)
        
        return document_ids
    
    def search_knowledge(self, client_id: str, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant knowledge for a client"""
        collection_name = f"client_{client_id}"
        try:
            collection = self.client.get_collection(collection_name)
        except:
            return []
        
        # Get query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'score': 1 - results['distances'][0][i] if results['distances'] else 0
            })
        
        return formatted_results