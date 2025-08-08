import os
import json
import pickle
import numpy as np
import openai
from typing import List, Dict, Tuple
import logging
from pathlib import Path
import re
import PyPDF2
import docx
import csv
import hashlib

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """Manages document processing and retrieval for RAG"""
    
    def __init__(self, knowledge_base_dir, embeddings_cache_dir, chunk_size=500, chunk_overlap=50, similarity_threshold=0.7):
        self.knowledge_base_dir = knowledge_base_dir
        self.embeddings_cache_dir = embeddings_cache_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        self.documents = []
        self.embeddings = []
        self.metadata = []
        
        # Create directories if they don't exist
        Path(self.knowledge_base_dir).mkdir(parents=True, exist_ok=True)
        Path(self.embeddings_cache_dir).mkdir(parents=True, exist_ok=True)
        
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load and process all documents in the knowledge base directory"""
        logger.info(f"Loading knowledge base from {self.knowledge_base_dir}")
        
        # Check for cached embeddings
        cache_file = os.path.join(self.embeddings_cache_dir, 'knowledge_base.pkl')
        
        # Get list of current files and their modification times
        current_files = self._get_file_signatures()
        
        # Load cache if it exists and is valid
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    if cached_data.get('file_signatures') == current_files:
                        self.documents = cached_data['documents']
                        self.embeddings = cached_data['embeddings']
                        self.metadata = cached_data['metadata']
                        logger.info(f"Loaded {len(self.documents)} cached document chunks")
                        return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        # Process all documents
        self._process_all_documents()
        
        # Cache the processed data
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings,
                    'metadata': self.metadata,
                    'file_signatures': current_files
                }, f)
            logger.info("Cached knowledge base embeddings")
        except Exception as e:
            logger.warning(f"Failed to cache embeddings: {e}")
    
    def _get_file_signatures(self) -> Dict:
        """Get signatures of all files in knowledge base for cache validation"""
        signatures = {}
        for file_path in Path(self.knowledge_base_dir).rglob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                signatures[str(file_path)] = {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime
                }
        return signatures
    
    def _process_all_documents(self):
        """Process all documents in the knowledge base directory"""
        supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.csv', '.json', '.md'}
        
        for file_path in Path(self.knowledge_base_dir).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    logger.info(f"Processing {file_path}")
                    content = self._extract_text(file_path)
                    chunks = self._chunk_text(content)
                    
                    for chunk in chunks:
                        self.documents.append(chunk)
                        self.metadata.append({
                            'source': str(file_path),
                            'filename': file_path.name,
                            'type': file_path.suffix
                        })
                    
                    logger.info(f"Processed {len(chunks)} chunks from {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
        
        # Generate embeddings for all documents
        if self.documents:
            logger.info(f"Generating embeddings for {len(self.documents)} chunks...")
            self.embeddings = self._generate_embeddings(self.documents)
            logger.info("Embeddings generated successfully")
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.txt' or suffix == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif suffix == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            
            elif suffix in ['.docx', '.doc']:
                doc = docx.Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            elif suffix == '.csv':
                text = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        text.append(' '.join(row))
                return '\n'.join(text)
            
            elif suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using OpenAI"""
        embeddings = []
        batch_size = 20  # Process in batches to avoid rate limits
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=batch
                )
                for item in response['data']:
                    embeddings.append(item['embedding'])
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                # Return empty embeddings for failed batch
                embeddings.extend([[0] * 1536 for _ in batch])
        
        return embeddings
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, Dict, float]]:
        """Search for relevant documents using semantic similarity"""
        if not self.documents:
            return []
        
        # Generate embedding for query
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=[query]
            )
            query_embedding = response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            if similarity >= self.similarity_threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for idx, similarity in similarities[:top_k]:
            results.append((
                self.documents[idx],
                self.metadata[idx],
                similarity
            ))
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def add_document(self, content: str, metadata: Dict):
        """Add a new document to the knowledge base"""
        chunks = self._chunk_text(content)
        new_embeddings = self._generate_embeddings(chunks)
        
        for chunk, embedding in zip(chunks, new_embeddings):
            self.documents.append(chunk)
            self.embeddings.append(embedding)
            self.metadata.append(metadata)
        
        # Update cache
        self._save_cache()
    
    def _save_cache(self):
        """Save the current knowledge base to cache"""
        cache_file = os.path.join(self.embeddings_cache_dir, 'knowledge_base.pkl')
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings,
                    'metadata': self.metadata,
                    'file_signatures': self._get_file_signatures()
                }, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")