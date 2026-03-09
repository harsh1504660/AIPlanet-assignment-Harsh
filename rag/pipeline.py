"""
RAG Pipeline for Math Mentor
Handles document chunking, embedding, vector storage, and retrieval
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import glob


class MathRAGPipeline:
    """RAG pipeline using sentence-transformers for embeddings and FAISS for vector storage."""

    def __init__(self, knowledge_base_path: str = "./knowledge_base", 
                 vector_store_path: str = "./rag/vector_store",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 top_k: int = 5):
        self.knowledge_base_path = knowledge_base_path
        self.vector_store_path = vector_store_path
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        
        self.documents = []
        self.embeddings = None
        self.index = None
        self.model = None
        self._initialized = False

    def _load_model(self):
        """Lazy load embedding model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.embedding_model_name)
            except Exception as e:
                print(f"Warning: Could not load sentence-transformers: {e}")
                self.model = None

    def chunk_text(self, text: str, source: str) -> List[Dict]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        
        i = 0
        chunk_id = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "id": f"{source}_{chunk_id}",
                "text": chunk_text,
                "source": source,
                "chunk_id": chunk_id
            })
            i += self.chunk_size - self.chunk_overlap
            chunk_id += 1
        
        return chunks

    def load_knowledge_base(self) -> List[Dict]:
        """Load all markdown files from knowledge base directory."""
        documents = []
        kb_path = Path(self.knowledge_base_path)
        
        if not kb_path.exists():
            print(f"Knowledge base path {kb_path} does not exist")
            return documents
        
        for md_file in kb_path.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = self.chunk_text(content, md_file.stem)
                documents.extend(chunks)
                print(f"Loaded {len(chunks)} chunks from {md_file.name}")
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
        
        return documents

    def build_index(self, force_rebuild: bool = False):
        """Build or load FAISS index."""
        index_path = Path(self.vector_store_path)
        index_file = index_path / "index.faiss"
        docs_file = index_path / "documents.json"
        
        # Try to load existing index
        if not force_rebuild and index_file.exists() and docs_file.exists():
            try:
                self._load_existing_index(index_file, docs_file)
                self._initialized = True
                return True
            except Exception as e:
                print(f"Could not load existing index: {e}. Rebuilding...")
        
        # Build new index
        return self._build_new_index(index_path, index_file, docs_file)

    def _build_new_index(self, index_path, index_file, docs_file):
        """Build a new FAISS index from knowledge base."""
        self._load_model()
        
        # Load documents
        self.documents = self.load_knowledge_base()
        if not self.documents:
            print("No documents loaded. Using fallback mode.")
            self._initialized = True
            return False
        
        # Generate embeddings
        texts = [doc["text"] for doc in self.documents]
        
        if self.model:
            try:
                import faiss
                self.embeddings = self.model.encode(texts, show_progress_bar=False)
                
                # Build FAISS index
                dimension = self.embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(self.embeddings.astype(np.float32))
                
                # Save index
                index_path.mkdir(parents=True, exist_ok=True)
                faiss.write_index(self.index, str(index_file))
                
                with open(docs_file, 'w') as f:
                    json.dump(self.documents, f, indent=2)
                
                print(f"Built index with {len(self.documents)} chunks")
                self._initialized = True
                return True
            except Exception as e:
                print(f"FAISS/embedding error: {e}. Using keyword search fallback.")
        
        self._initialized = True
        return False

    def _load_existing_index(self, index_file, docs_file):
        """Load existing FAISS index."""
        import faiss
        self._load_model()
        
        self.index = faiss.read_index(str(index_file))
        with open(docs_file, 'r') as f:
            self.documents = json.load(f)
        
        print(f"Loaded existing index with {len(self.documents)} chunks")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve relevant chunks for a query."""
        if not self._initialized:
            self.build_index()
        
        k = top_k or self.top_k
        
        # Try semantic search with FAISS
        if self.index is not None and self.model is not None:
            try:
                query_embedding = self.model.encode([query])
                distances, indices = self.index.search(query_embedding.astype(np.float32), k)
                
                results = []
                for idx, dist in zip(indices[0], distances[0]):
                    if idx < len(self.documents):
                        doc = self.documents[idx].copy()
                        doc["score"] = float(1 / (1 + dist))  # Convert distance to similarity
                        results.append(doc)
                
                return results
            except Exception as e:
                print(f"Semantic search failed: {e}. Falling back to keyword search.")
        
        # Fallback: keyword search
        return self._keyword_search(query, k)

    def _keyword_search(self, query: str, k: int) -> List[Dict]:
        """Simple keyword-based search fallback."""
        if not self.documents:
            return []
        
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in self.documents:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                score = overlap / len(query_words)
                scored_doc = doc.copy()
                scored_doc["score"] = score
                scored_docs.append(scored_doc)
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:k]

    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved documents into a context string."""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get("source", "unknown").replace("_", " ").title()
            context_parts.append(f"[Source {i}: {source}]\n{doc['text']}")
        
        return "\n\n".join(context_parts)

    def get_sources_summary(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Get a summary of retrieved sources for display."""
        sources = []
        for doc in retrieved_docs:
            sources.append({
                "source": doc.get("source", "unknown").replace("_", " ").title(),
                "preview": doc["text"][:150] + "..." if len(doc["text"]) > 150 else doc["text"],
                "score": round(doc.get("score", 0), 3)
            })
        return sources
