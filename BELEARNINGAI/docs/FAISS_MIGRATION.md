# Migration từ ChromaDB sang FAISS

## Tại sao chuyển sang FAISS?

Dự án của bạn gặp lỗi khi cài đặt `hnswlib` - một dependency của ChromaDB:

```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"
```

**FAISS** (Facebook AI Similarity Search) là giải pháp tốt hơn vì:

✅ **No Build Required**: Có sẵn pre-built wheels cho Windows  
✅ **Faster Performance**: Nhanh hơn ChromaDB đáng kể  
✅ **Production Ready**: Được Facebook sử dụng trong production  
✅ **Memory Efficient**: Tối ưu cho large-scale datasets  
✅ **Multiple Algorithms**: Hỗ trợ nhiều thuật toán similarity search  

## Các thay đổi đã thực hiện

### 1. Cập nhật `requirements.txt`
```diff
- chromadb==0.5.18                   # Vector database for RAG
- hnswlib==0.8.0                     # Fast similarity search (ChromaDB dependency)
+ faiss-cpu==1.9.0                   # Facebook AI Similarity Search - CPU version
+ numpy>=1.24.0                      # Required for FAISS vector operations
```

### 2. Tạo `services/faiss_vector_service.py`
- Implementation mới với FAISS
- Compatible interface giống ChromaDB
- Persistent storage với pickle + JSON
- Cosine similarity search

### 3. Cập nhật `services/vector_service.py`
- Auto-fallback: FAISS first, ChromaDB second
- Singleton pattern được giữ nguyên

### 4. Cập nhật `config/config.py`
```python
# Vector Database Settings
vector_db_type: str = Field(default="faiss")
vector_persist_directory: str = Field(default="./faiss_db")
```

### 5. Cập nhật health check
- Hỗ trợ kiểm tra cả FAISS và ChromaDB
- Fallback mechanism

## Hướng dẫn cài đặt

### Bước 1: Gỡ packages cũ (optional)
```powershell
pip uninstall chromadb hnswlib -y
```

### Bước 2: Cài đặt FAISS và dependencies
```powershell
pip install faiss-cpu==1.9.0 numpy>=1.24.0
```

### Bước 3: Cài đặt tất cả requirements
```powershell
pip install -r requirements.txt
```

### Bước 4: Test cài đặt
```powershell
python -c "import faiss; import numpy; print('FAISS installed successfully!')"
```

### Bước 5: Chạy health check
```powershell
python scripts/health_check.py
```

## Migration data (nếu có ChromaDB data cũ)

Nếu bạn đã có data trong ChromaDB và muốn migrate sang FAISS:

### Script migrate tự động:
```python
# scripts/migrate_chromadb_to_faiss.py
import asyncio
from services.vector_service import vector_service
from services.faiss_vector_service import FAISSVectorService

async def migrate_chromadb_to_faiss():
    # TODO: Implement migration logic
    pass

if __name__ == "__main__":
    asyncio.run(migrate_chromadb_to_faiss())
```

## Testing

### Test FAISS service:
```python
import asyncio
from services.faiss_vector_service import FAISSVectorService

async def test_faiss():
    service = FAISSVectorService()
    
    # Test upsert
    vectors = [{
        "id": "test-1",
        "values": [0.1] * 768,
        "metadata": {"text": "Test document"}
    }]
    
    result = await service.upsert_vectors(vectors)
    print(f"Upsert: {result}")
    
    # Test search
    results = await service.search([0.1] * 768, top_k=1)
    print(f"Search: {results}")

asyncio.run(test_faiss())
```

## Performance Comparison

| Metric | ChromaDB | FAISS |
|--------|----------|-------|
| Setup | Cần build tools | Pre-built wheels |
| Speed | Fast | **Faster** |
| Memory | Good | **Better** |
| Scalability | Good | **Excellent** |
| Windows Support | ❌ Build issues | ✅ Native support |

## API Compatibility

FAISS service có **identical interface** với ChromaDB service:

```python
# Tất cả APIs này work giống nhau
await vector_service.upsert_vectors(vectors, namespace="courses")
await vector_service.search(query_vector, top_k=5, namespace="courses")
await vector_service.delete_by_filter({"course_id": "123"}, namespace="courses")
await vector_service.get_collection_stats(namespace="courses")
await vector_service.reset_collection(namespace="courses")
```

## Troubleshooting

### Lỗi "FAISS not installed"
```powershell
pip install faiss-cpu==1.9.0
```

### Lỗi "numpy not found"
```powershell
pip install numpy>=1.24.0
```

### Fallback to ChromaDB
Nếu FAISS không hoạt động, system sẽ tự động fallback về ChromaDB (nếu có).

### Performance tuning
```python
# Trong config.py, có thể tune:
vector_db_type: str = "faiss"  # hoặc "chromadb"
vector_persist_directory: str = "./faiss_db"
```

## Next Steps

1. **Install FAISS**: `pip install faiss-cpu numpy`
2. **Test health check**: `python scripts/health_check.py`
3. **Run your app**: Sẽ tự động sử dụng FAISS
4. **Monitor performance**: FAISS sẽ nhanh hơn và ổn định hơn

## Support

Nếu gặp vấn đề:
1. Check `pip list | grep faiss`
2. Run health check
3. Check logs for "Vector Service" messages
4. FAISS docs: https://github.com/facebookresearch/faiss