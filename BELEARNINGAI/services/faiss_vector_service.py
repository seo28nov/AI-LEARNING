"""
FAISS Vector Service - Thay thế ChromaDB với Facebook AI Similarity Search.

FAISS được chọn làm vector database cho BeLearning vì:
✅ No compile required - có sẵn pre-built wheels cho Windows
✅ Facebook AI production-ready - được sử dụng rộng rãi
✅ Extremely fast - nhanh hơn ChromaDB đáng kể  
✅ Local storage - không phụ thuộc cloud, data stays on-premise
✅ Free & open source - không có chi phí định kỳ
✅ Memory efficient - tối ưu cho large-scale datasets
✅ Multiple index types - hỗ trợ nhiều thuật toán tìm kiếm
✅ Python native - integration mượt mà với FastAPI

FAISS phù hợp với educational platform vì:
- Scale excellent cho hàng nghìn courses
- Performance vượt trội cho real-time search
- Cost-effective cho institutions
- Self-hosted - full control over data
"""
import logging
import pickle
import json
import os
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from config.config import settings

logger = logging.getLogger(__name__)


class FAISSVectorService:
    """
    Vector database service sử dụng FAISS.
    
    FAISS lưu trữ embeddings trong memory và trên disk, cung cấp
    similarity search cực nhanh với cosine similarity hoặc L2 distance.
    """
    
    def __init__(self):
        """
        Khởi tạo FAISS vector service.
        
        Sử dụng persistent storage để data không mất khi restart.
        """
        if faiss is None:
            raise ImportError("FAISS is not installed. Please install: pip install faiss-cpu")
            
        try:
            # Lấy persist directory từ settings
            self.persist_directory = getattr(settings, "vector_persist_directory", "./faiss_db")
            
            # Tạo directory nếu chưa có
            os.makedirs(self.persist_directory, exist_ok=True)
            
            logger.info(f"🔧 Initializing FAISS with persist_directory: {self.persist_directory}")
            
            # Dictionary để lưu các collections (namespaces)
            self.collections = {}
            
            # Load existing collections
            self._load_collections()
            
            logger.info("✅ FAISS Vector Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize FAISS: {e}")
            raise
    
    def _get_collection_path(self, namespace: str) -> Dict[str, str]:
        """Lấy file paths cho collection."""
        safe_name = namespace.replace("/", "_").replace(" ", "_")
        return {
            "index": os.path.join(self.persist_directory, f"{safe_name}.index"),
            "metadata": os.path.join(self.persist_directory, f"{safe_name}.metadata"),
            "ids": os.path.join(self.persist_directory, f"{safe_name}.ids")
        }
    
    def _load_collections(self):
        """Load tất cả collections từ disk."""
        try:
            for file in os.listdir(self.persist_directory):
                if file.endswith(".index"):
                    namespace = file[:-6]  # Remove .index extension
                    self._load_collection(namespace)
        except Exception as e:
            logger.warning(f"⚠️ Error loading collections: {e}")
    
    def _load_collection(self, namespace: str):
        """Load một collection từ disk."""
        try:
            paths = self._get_collection_path(namespace)
            
            if os.path.exists(paths["index"]):
                # Load FAISS index
                index = faiss.read_index(paths["index"])
                
                # Load metadata
                metadata = {}
                if os.path.exists(paths["metadata"]):
                    with open(paths["metadata"], 'rb') as f:
                        metadata = pickle.load(f)
                
                # Load IDs
                ids = []
                if os.path.exists(paths["ids"]):
                    with open(paths["ids"], 'r', encoding='utf-8') as f:
                        ids = json.load(f)
                
                self.collections[namespace] = {
                    "index": index,
                    "metadata": metadata,
                    "ids": ids,
                    "dimension": index.d
                }
                
                logger.info(f"✅ Loaded collection '{namespace}' with {len(ids)} vectors")
        except Exception as e:
            logger.error(f"❌ Error loading collection '{namespace}': {e}")
    
    def _save_collection(self, namespace: str):
        """Save một collection xuống disk."""
        try:
            if namespace not in self.collections:
                return
                
            paths = self._get_collection_path(namespace)
            collection = self.collections[namespace]
            
            # Save FAISS index
            faiss.write_index(collection["index"], paths["index"])
            
            # Save metadata
            with open(paths["metadata"], 'wb') as f:
                pickle.dump(collection["metadata"], f)
            
            # Save IDs
            with open(paths["ids"], 'w', encoding='utf-8') as f:
                json.dump(collection["ids"], f, ensure_ascii=False, indent=2)
                
            logger.debug(f"💾 Saved collection '{namespace}'")
        except Exception as e:
            logger.error(f"❌ Error saving collection '{namespace}': {e}")
    
    def _get_or_create_collection(self, namespace: str, dimension: int = 768):
        """
        Get hoặc create collection trong FAISS.
        
        Args:
            namespace: Tên collection
            dimension: Dimension của embedding vectors
            
        Returns:
            Collection dict với index, metadata, ids
        """
        try:
            if namespace in self.collections:
                return self.collections[namespace]
            
            # Create new collection
            # Sử dụng IndexFlatIP cho cosine similarity (Inner Product)
            # Note: Với normalized vectors, IP = cosine similarity
            index = faiss.IndexFlatIP(dimension)
            
            self.collections[namespace] = {
                "index": index,
                "metadata": {},  # Dict[id -> metadata]
                "ids": [],  # List of IDs theo thứ tự trong index
                "dimension": dimension
            }
            
            logger.info(f"✅ Created new collection '{namespace}' with dimension {dimension}")
            
            return self.collections[namespace]
            
        except Exception as e:
            logger.error(f"❌ Error getting/creating collection '{namespace}': {e}")
            raise
    
    def _normalize_vector(self, vector: List[float]) -> np.ndarray:
        """Normalize vector để sử dụng với cosine similarity."""
        vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.reshape(1, -1)
    
    async def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = "courses"
    ) -> Dict[str, Any]:
        """
        Insert hoặc update vectors vào FAISS.
        
        Args:
            vectors: List of dicts với format giống ChromaDB
            namespace: Collection name
            
        Returns:
            Dict với thông tin upsert
        """
        try:
            if not vectors:
                logger.warning("⚠️ No vectors to upsert")
                return {
                    "success": False,
                    "upserted_count": 0,
                    "namespace": namespace,
                    "error": "No vectors provided"
                }
            
            logger.info(f"📊 Upserting {len(vectors)} vectors to namespace '{namespace}'")
            
            # Get dimension từ vector đầu tiên
            dimension = len(vectors[0]["values"])
            
            # Get hoặc create collection
            collection = self._get_or_create_collection(namespace, dimension)
            
            # Prepare data
            new_vectors = []
            new_ids = []
            new_metadata = {}
            
            for vector in vectors:
                vector_id = vector["id"]
                values = vector["values"]
                metadata = vector.get("metadata", {})
                
                # Check nếu ID đã tồn tại - nếu có thì update
                if vector_id in collection["ids"]:
                    # Update existing vector
                    # FAISS không hỗ trợ update trực tiếp, chỉ update metadata
                    collection["metadata"][vector_id] = metadata
                    # Note: Vector values không thể update, phải delete rồi add lại
                    # hoặc rebuild toàn bộ index. Hiện tại chỉ update metadata.
                else:
                    # Add new vector
                    normalized_vec = self._normalize_vector(values)
                    new_vectors.append(normalized_vec[0])
                    new_ids.append(vector_id)
                    new_metadata[vector_id] = metadata
            
            # Add new vectors to index
            if new_vectors:
                vectors_array = np.array(new_vectors, dtype=np.float32)
                collection["index"].add(vectors_array)
                
                # Update IDs và metadata
                collection["ids"].extend(new_ids)
                collection["metadata"].update(new_metadata)
            
            # Save to disk
            self._save_collection(namespace)
            
            logger.info(f"✅ Successfully upserted {len(vectors)} vectors")
            
            return {
                "success": True,
                "upserted_count": len(vectors),
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {e}")
            return {
                "success": False,
                "upserted_count": 0,
                "namespace": namespace,
                "error": str(e)
            }
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: str = "courses",
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vectors tương tự trong FAISS.
        
        Args:
            query_vector: Query embedding vector
            top_k: Số kết quả trả về
            namespace: Collection name
            filter_dict: Metadata filters (sẽ filter sau khi search)
            
        Returns:
            List of results với format giống ChromaDB
        """
        try:
            logger.info(f"🔍 Searching in namespace '{namespace}' with top_k={top_k}")
            
            if namespace not in self.collections:
                logger.warning(f"⚠️ Collection '{namespace}' not found")
                return []
            
            collection = self.collections[namespace]
            
            if len(collection["ids"]) == 0:
                logger.warning(f"⚠️ Collection '{namespace}' is empty")
                return []
            
            # Normalize query vector
            query_vec = self._normalize_vector(query_vector)
            
            # Search trong FAISS index
            # Lấy nhiều hơn top_k để có thể filter
            search_k = min(top_k * 3, len(collection["ids"]))
            scores, indices = collection["index"].search(query_vec, search_k)
            
            # Format results
            results = []
            
            for i, idx in enumerate(indices[0]):
                if idx == -1:  # FAISS trả về -1 khi không tìm thấy
                    continue
                
                vector_id = collection["ids"][idx]
                score = float(scores[0][i])  # Cosine similarity score
                metadata = collection["metadata"].get(vector_id, {})
                
                # Apply filter nếu có
                if filter_dict:
                    match = all(
                        metadata.get(key) == value
                        for key, value in filter_dict.items()
                    )
                    if not match:
                        continue
                
                results.append({
                    "id": vector_id,
                    "score": score,
                    "metadata": metadata
                })
                
                # Dừng khi đã có đủ top_k results
                if len(results) >= top_k:
                    break
            
            logger.info(f"✅ Found {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching vectors: {e}")
            return []
    
    async def delete_by_filter(
        self,
        filter_dict: Dict[str, Any],
        namespace: str = "courses"
    ) -> Dict[str, Any]:
        """
        Xóa vectors theo metadata filter.
        
        Note: FAISS không hỗ trợ delete trực tiếp, phải rebuild index.
        """
        try:
            logger.info(f"🗑️ Deleting vectors in '{namespace}' with filter: {filter_dict}")
            
            if namespace not in self.collections:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "namespace": namespace
                }
            
            collection = self.collections[namespace]
            
            # Find IDs to delete
            ids_to_delete = []
            for vector_id in collection["ids"]:
                metadata = collection["metadata"].get(vector_id, {})
                match = all(
                    metadata.get(key) == value
                    for key, value in filter_dict.items()
                )
                if match:
                    ids_to_delete.append(vector_id)
            
            if not ids_to_delete:
                logger.info("⚠️ No vectors found matching filter")
                return {
                    "success": True,
                    "deleted_count": 0,
                    "namespace": namespace
                }
            
            # Rebuild index without deleted vectors
            remaining_vectors = []
            remaining_ids = []
            remaining_metadata = {}
            
            for i, vector_id in enumerate(collection["ids"]):
                if vector_id not in ids_to_delete:
                    # Get vector from index
                    vector = collection["index"].reconstruct(i)
                    remaining_vectors.append(vector)
                    remaining_ids.append(vector_id)
                    remaining_metadata[vector_id] = collection["metadata"][vector_id]
            
            # Create new index
            new_index = faiss.IndexFlatIP(collection["dimension"])
            if remaining_vectors:
                vectors_array = np.array(remaining_vectors, dtype=np.float32)
                new_index.add(vectors_array)
            
            # Update collection
            collection["index"] = new_index
            collection["ids"] = remaining_ids
            collection["metadata"] = remaining_metadata
            
            # Save
            self._save_collection(namespace)
            
            logger.info(f"✅ Deleted {len(ids_to_delete)} vectors")
            
            return {
                "success": True,
                "deleted_count": len(ids_to_delete),
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting vectors: {e}")
            return {
                "success": False,
                "deleted_count": 0,
                "namespace": namespace,
                "error": str(e)
            }
    
    async def get_collection_stats(self, namespace: str = "courses") -> Dict[str, Any]:
        """
        Lấy thống kê về collection.
        """
        try:
            if namespace not in self.collections:
                return {
                    "name": namespace,
                    "count": 0,
                    "error": "Collection not found"
                }
            
            collection = self.collections[namespace]
            
            return {
                "name": namespace,
                "count": len(collection["ids"]),
                "dimension": collection["dimension"],
                "metadata": {
                    "index_type": "IndexFlatIP",
                    "similarity_metric": "cosine"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {
                "name": namespace,
                "count": 0,
                "error": str(e)
            }
    
    async def reset_collection(self, namespace: str = "courses") -> Dict[str, Any]:
        """
        Xóa toàn bộ collection (dùng cho testing/reset).
        """
        try:
            logger.warning(f"⚠️ Resetting collection '{namespace}'")
            
            if namespace in self.collections:
                del self.collections[namespace]
            
            # Delete files
            paths = self._get_collection_path(namespace)
            for path in paths.values():
                if os.path.exists(path):
                    os.remove(path)
            
            logger.info(f"✅ Collection '{namespace}' reset successfully")
            
            return {
                "success": True,
                "message": f"Collection '{namespace}' deleted"
            }
            
        except Exception as e:
            logger.error(f"❌ Error resetting collection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def __del__(self):
        """Cleanup khi service bị destroy."""
        try:
            # Save tất cả collections
            for namespace in self.collections:
                self._save_collection(namespace)
        except Exception as e:
            # Log lỗi để debug, không silent fail
            logger.error(f"❌ Failed to save collections on shutdown: {e}")


# ============================================================================
# SINGLETON INSTANCE  
# ============================================================================

# Khởi tạo FAISS vector service
try:
    vector_service = FAISSVectorService()
    logger.info("✅ FAISS Vector Service singleton initialized")
except Exception as e:
    logger.error(f"❌ Cannot initialize FAISS Vector Service: {e}")
    vector_service = None