"""
Test script để kiểm tra FAISS installation và functionality.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_faiss_installation():
    """Test FAISS installation."""
    print("🧪 Testing FAISS installation...")
    
    try:
        import faiss
        print("  ✅ FAISS imported successfully")
        
        # Get version if available
        version = getattr(faiss, '__version__', 'unknown')
        print(f"  ✅ FAISS version: {version}")
        
        return True
    except ImportError as e:
        print(f"  ❌ FAISS import failed: {e}")
        return False

def test_numpy_installation():
    """Test NumPy installation."""
    print("\n🧪 Testing NumPy installation...")
    
    try:
        import numpy as np
        print("  ✅ NumPy imported successfully")
        print(f"  ✅ NumPy version: {np.__version__}")
        
        return True
    except ImportError as e:
        print(f"  ❌ NumPy import failed: {e}")
        return False

def test_faiss_basic_operations():
    """Test basic FAISS operations."""
    print("\n🧪 Testing FAISS basic operations...")
    
    try:
        import faiss
        import numpy as np
        
        # Create a simple index
        dimension = 768  # Common embedding dimension
        index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        
        print(f"  ✅ Created FAISS index (dimension: {dimension})")
        
        # Create test data
        n_vectors = 10
        vectors = np.random.rand(n_vectors, dimension).astype(np.float32)
        
        # Normalize vectors for cosine similarity
        for i in range(n_vectors):
            vectors[i] = vectors[i] / np.linalg.norm(vectors[i])
        
        # Add vectors to index
        index.add(vectors)
        print(f"  ✅ Added {n_vectors} vectors to index")
        
        # Test search
        query_vector = vectors[0:1]  # Use first vector as query
        k = 3
        scores, indices = index.search(query_vector, k)
        
        print(f"  ✅ Search completed: found {len(indices[0])} results")
        print(f"  ✅ Top similarity score: {scores[0][0]:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAISS operations failed: {e}")
        return False

def test_faiss_service():
    """Test custom FAISS service."""
    print("\n🧪 Testing FAISS Vector Service...")
    
    try:
        from services.faiss_vector_service import FAISSVectorService
        
        # Create service
        _ = FAISSVectorService()
        print("  ✅ FAISS Vector Service created")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAISS Vector Service failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FAISS Installation & Functionality Test")
    print("=" * 60)
    
    results = []
    
    # Test installations
    results.append(("FAISS Installation", test_faiss_installation()))
    results.append(("NumPy Installation", test_numpy_installation()))
    
    # Test operations
    results.append(("FAISS Basic Operations", test_faiss_basic_operations()))
    results.append(("FAISS Vector Service", test_faiss_service()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FAISS is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)