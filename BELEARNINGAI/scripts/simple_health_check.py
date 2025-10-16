"""
Simple health check để kiểm tra FAISS Vector Database.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_faiss_only():
    """Test FAISS installation mà không cần dependencies khác."""
    print("🧪 Testing FAISS (standalone)...")
    
    try:
        import faiss
        import numpy as np
        
        print(f"  ✅ FAISS version: {getattr(faiss, '__version__', 'unknown')}")
        print(f"  ✅ NumPy version: {np.__version__}")
        
        # Test basic FAISS operations
        dimension = 768
        index = faiss.IndexFlatIP(dimension)
        
        # Create test vector
        test_vector = np.random.rand(1, dimension).astype(np.float32)
        # Normalize for cosine similarity
        test_vector = test_vector / np.linalg.norm(test_vector)
        
        # Add to index
        index.add(test_vector)
        
        # Search
        scores, indices = index.search(test_vector, 1)
        
        print(f"  ✅ FAISS test successful (score: {scores[0][0]:.3f})")
        return True
        
    except Exception as e:
        print(f"  ❌ FAISS test failed: {e}")
        return False

async def test_vector_service_simple():
    """Test vector service với minimal dependencies."""
    print("\n🧪 Testing Vector Service (simple)...")
    
    try:
        # Test imports one by one
        print("  📦 Testing imports...")
        
        try:
            from config.config import get_settings
            print("    ✅ Config import OK")
        except Exception as e:
            print(f"    ❌ Config import failed: {e}")
            return False
        
        try:
            from services.faiss_vector_service import FAISSVectorService
            print("    ✅ FAISS service import OK")
        except Exception as e:
            print(f"    ❌ FAISS service import failed: {e}")
            return False
        
        # Try to create service
        settings = get_settings()
        print(f"  📁 Persist directory: {settings.vector_persist_directory}")
        
        service = FAISSVectorService()
        print("  ✅ FAISS Vector Service created")
        
        # Test basic functionality
        stats = await service.get_collection_stats("test")
        print(f"  ✅ Collection stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vector Service test failed: {e}")
        import traceback
        print(f"  📋 Full error: {traceback.format_exc()}")
        return False

async def main():
    """Main function."""
    print("=" * 60)
    print("🚀 Simple FAISS Health Check")
    print("=" * 60)
    
    # Test 1: FAISS standalone
    faiss_ok = test_faiss_only()
    
    # Test 2: Vector service
    service_ok = await test_vector_service_simple()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Results Summary")  
    print("=" * 60)
    
    print(f"  {'✅' if faiss_ok else '❌'} FAISS Standalone")
    print(f"  {'✅' if service_ok else '❌'} Vector Service")
    
    overall = faiss_ok and service_ok
    print(f"\n🎯 Overall: {'✅ SUCCESS' if overall else '❌ FAILED'}")
    
    if overall:
        print("🎉 FAISS Vector Database is ready!")
    else:
        print("⚠️ Some issues found. Check the logs above.")
    
    return overall

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)