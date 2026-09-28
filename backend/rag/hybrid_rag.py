"""
ReturnIQ Hybrid RAG System
Combines Semantic Search (40%) + Keyword Search (40%) + Knowledge Graph (20%)
"""

import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class HybridRAG:
    """Hybrid Retrieval-Augmented Generation System"""

    def __init__(self):
        self.semantic_db = SemanticVectorDB()
        self.keyword_search = KeywordSearchEngine()
        self.knowledge_graph = KnowledgeGraph()
        self.initialized = False

    def initialize(self):
        """Initialize all RAG components"""
        try:
            self.semantic_db.initialize()
            self.keyword_search.initialize()
            self.knowledge_graph.initialize()
            self.initialized = True
            logger.info("Hybrid RAG system initialized")
        except Exception as e:
            logger.error(f"RAG initialization error: {str(e)}")
            raise

    def is_initialized(self) -> bool:
        return self.initialized

    def retrieve_context(self, return_data: Dict, top_k: int = 5) -> Dict:
        """
        Retrieve context using hybrid approach:
        40% Semantic (vector similarity)
        40% Keyword (BM25)
        20% Knowledge Graph (relationships)
        """
        try:
            # 1. Semantic Search (40%)
            semantic_results = self.semantic_db.similarity_search(
                query=return_data.get('return_reason', ''),
                customer_comments=return_data.get('customer_comments', ''),
                top_k=int(top_k * 0.4)
            )

            # 2. Keyword Search (40%)
            keyword_results = self.keyword_search.search(
                query=return_data.get('return_reason', ''),
                product_id=return_data.get('product_id'),
                supplier_id=return_data.get('supplier_id'),
                top_k=int(top_k * 0.4)
            )

            # 3. Knowledge Graph (20%)
            kg_results = self.knowledge_graph.find_related_returns(
                product_id=return_data.get('product_id'),
                supplier_id=return_data.get('supplier_id'),
                customer_segment=return_data.get('customer_segment'),
                depth=2,
                limit=int(top_k * 0.2)
            )

            # Combine and rerank
            combined_results = self._combine_and_rerank(
                semantic_results,
                keyword_results,
                kg_results
            )

            return {
                "retrieved_returns": combined_results[:top_k],
                "retrieval_stats": {
                    "semantic_count": len(semantic_results),
                    "keyword_count": len(keyword_results),
                    "kg_count": len(kg_results),
                    "total_retrieved": len(combined_results)
                }
            }

        except Exception as e:
            logger.error(f"RAG retrieval error: {str(e)}")
            return {
                "retrieved_returns": [],
                "retrieval_stats": {"error": str(e)}
            }

    def index_return(self, return_data: Dict):
        """Add a return to all RAG indices"""
        try:
            # Index to semantic DB
            self.semantic_db.add_document(return_data)

            # Index to keyword search
            self.keyword_search.add_document(return_data)

            # Add to knowledge graph
            self.knowledge_graph.add_node(return_data)

        except Exception as e:
            logger.error(f"RAG indexing error: {str(e)}")
            raise

    def _combine_and_rerank(self, semantic_results: List, keyword_results: List, kg_results: List) -> List:
        """Combine results from 3 sources and rerank by relevance"""
        # Create unified score
        scored_results = defaultdict(lambda: {"result": None, "scores": []})

        # Add semantic scores (0.40 weight)
        for i, result in enumerate(semantic_results):
            result_id = result['id']
            score = (len(semantic_results) - i) / len(semantic_results) * 0.40  # Decay by rank
            scored_results[result_id]["result"] = result
            scored_results[result_id]["scores"].append(score)

        # Add keyword scores (0.40 weight)
        for i, result in enumerate(keyword_results):
            result_id = result['id']
            score = (len(keyword_results) - i) / len(keyword_results) * 0.40
            if scored_results[result_id]["result"] is None:
                scored_results[result_id]["result"] = result
            scored_results[result_id]["scores"].append(score)

        # Add KG scores (0.20 weight)
        for i, result in enumerate(kg_results):
            result_id = result['id']
            score = (len(kg_results) - i) / len(kg_results) * 0.20
            if scored_results[result_id]["result"] is None:
                scored_results[result_id]["result"] = result
            scored_results[result_id]["scores"].append(score)

        # Calculate final score and sort
        final_results = []
        for result_id, data in scored_results.items():
            final_score = sum(data["scores"]) / len(data["scores"])
            final_results.append({
                **data["result"],
                "combined_score": final_score
            })

        return sorted(final_results, key=lambda x: x["combined_score"], reverse=True)


class SemanticVectorDB:
    """Vector database for semantic similarity search"""

    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.embedding_model = "text-embedding-3-small"

    def initialize(self):
        """Initialize vector DB"""
        logger.info("Initializing semantic vector DB")
        # In production: connect to Pinecone, Weaviate, or Milvus

    def add_document(self, return_data: Dict):
        """Add return to vector DB"""
        try:
            # Create text for embedding
            text = f"{return_data.get('return_reason', '')} {return_data.get('customer_comments', '')}"

            # Generate embedding (mock for demo)
            embedding = self._generate_embedding(text)

            self.documents.append({
                "id": return_data.get('id'),
                "text": text,
                "return_data": return_data
            })
            self.embeddings.append(embedding)

        except Exception as e:
            logger.error(f"Vector DB add error: {str(e)}")

    def similarity_search(self, query: str, customer_comments: str = "", top_k: int = 5) -> List[Dict]:
        """Search by semantic similarity"""
        try:
            search_text = f"{query} {customer_comments}"
            query_embedding = self._generate_embedding(search_text)

            # Calculate cosine similarity
            similarities = []
            for i, doc_embedding in enumerate(self.embeddings):
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((i, similarity))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Return top_k
            results = []
            for idx, similarity in similarities[:top_k]:
                doc = self.documents[idx]
                results.append({
                    "id": doc["id"],
                    "return_data": doc["return_data"],
                    "similarity_score": float(similarity),
                    "source": "semantic"
                })

            return results

        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text (mock implementation)"""
        # In production: call OpenAI or use HuggingFace
        # Mock: hash-based deterministic embedding
        import hashlib
        hash_val = hashlib.md5(text.encode()).digest()
        return np.frombuffer(hash_val, dtype=np.uint8).astype(np.float32) / 255.0

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class KeywordSearchEngine:
    """BM25 keyword search (like Elasticsearch)"""

    def __init__(self):
        self.documents = []
        self.index = defaultdict(list)  # word -> [doc_ids]

    def initialize(self):
        """Initialize keyword search engine"""
        logger.info("Initializing keyword search engine")

    def add_document(self, return_data: Dict):
        """Add return to keyword index"""
        try:
            doc_id = return_data.get('id')
            text = f"{return_data.get('return_reason', '')} {return_data.get('customer_comments', '')}"

            self.documents.append({
                "id": doc_id,
                "text": text,
                "return_data": return_data,
                "product_id": return_data.get('product_id'),
                "supplier_id": return_data.get('supplier_id')
            })

            # Index words
            words = self._tokenize(text)
            for word in words:
                self.index[word].append(doc_id)

        except Exception as e:
            logger.error(f"Keyword index error: {str(e)}")

    def search(self, query: str, product_id: str = None, supplier_id: str = None, top_k: int = 5) -> List[Dict]:
        """Search by keywords (BM25)"""
        try:
            query_words = self._tokenize(query)

            # Calculate BM25 scores
            scores = defaultdict(float)

            for word in query_words:
                matching_docs = self.index.get(word, [])
                idf = np.log(len(self.documents) / (1 + len(matching_docs)))  # IDF

                for doc_id in matching_docs:
                    scores[doc_id] += idf

            # Apply product/supplier filters
            if product_id:
                for doc in self.documents:
                    if doc["product_id"] != product_id:
                        scores[doc["id"]] *= 0.5  # Downrank

            # Sort by score
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            results = []
            for doc_id, score in sorted_results[:top_k]:
                doc = next((d for d in self.documents if d["id"] == doc_id), None)
                if doc:
                    results.append({
                        "id": doc["id"],
                        "return_data": doc["return_data"],
                        "bm25_score": float(score),
                        "source": "keyword"
                    })

            return results

        except Exception as e:
            logger.error(f"Keyword search error: {str(e)}")
            return []

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text (basic implementation)"""
        return text.lower().split()


class KnowledgeGraph:
    """Knowledge graph for relationship-based retrieval"""

    def __init__(self):
        self.nodes = {}  # id -> node data
        self.edges = defaultdict(list)  # source_id -> [target_ids]

    def initialize(self):
        """Initialize knowledge graph"""
        logger.info("Initializing knowledge graph")

    def add_node(self, return_data: Dict):
        """Add return as node in graph"""
        try:
            node_id = return_data.get('id')

            self.nodes[node_id] = {
                "id": node_id,
                "return_data": return_data,
                "type": "return",
                "product_id": return_data.get('product_id'),
                "supplier_id": return_data.get('supplier_id'),
                "customer_id": return_data.get('customer_id')
            }

            # Create edges to related returns
            self._create_edges(node_id, return_data)

        except Exception as e:
            logger.error(f"KG node add error: {str(e)}")

    def find_related_returns(self, product_id: str, supplier_id: str, customer_segment: str, depth: int = 2, limit: int = 5) -> List[Dict]:
        """Find related returns by graph traversal"""
        try:
            related = set()

            # Find returns with same product
            for node_id, node in self.nodes.items():
                if node["product_id"] == product_id:
                    related.add(node_id)

            # Find returns from same supplier
            for node_id, node in self.nodes.items():
                if node["supplier_id"] == supplier_id:
                    related.add(node_id)

            # Find returns from same customer segment
            for node_id, node in self.nodes.items():
                if node["return_data"].get('customer_segment') == customer_segment:
                    related.add(node_id)

            # Convert to results
            results = []
            for node_id in list(related)[:limit]:
                results.append({
                    "id": node_id,
                    "return_data": self.nodes[node_id]["return_data"],
                    "graph_score": 0.85,
                    "source": "knowledge_graph"
                })

            return results

        except Exception as e:
            logger.error(f"KG traversal error: {str(e)}")
            return []

    def _create_edges(self, source_id: str, return_data: Dict):
        """Create edges in knowledge graph"""
        # Edge to other returns with same product
        for node_id, node in self.nodes.items():
            if node["product_id"] == return_data.get('product_id'):
                self.edges[source_id].append(node_id)

            # Edge to other returns from same supplier
            if node["supplier_id"] == return_data.get('supplier_id'):
                self.edges[source_id].append(node_id)
