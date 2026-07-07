import sys
import os
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, PointStruct, SparseVector

def test_qdrant_connection():
    print("=" * 60)
    print("QDRANT VECTOR DATABASE DIAGNOSTIC UTILITY")
    print("=" * 60)
    
    # 1. Check Configuration
    print(f"[+] Loaded .env file: {os.path.exists('.env')}")
    host = settings.qdrant.host or os.environ.get("QDRANT_HOST") or "localhost"
    port = int(settings.qdrant.port or os.environ.get("QDRANT_PORT") or 6333)
    collection_name = settings.qdrant.collection_name or os.environ.get("QDRANT_COLLECTION_NAME") or "nova-policies"
    api_key = settings.qdrant.api_key or os.environ.get("QDRANT_API_KEY")
    
    print(f"[+] Target Host: {host}")
    print(f"[+] Target Port: {port}")
    print(f"[+] Target Collection: {collection_name}")
    
    # 2. Initialize client
    print("\n[~] Connecting to Qdrant...")
    try:
        client = QdrantClient(host=host, port=port, api_key=api_key)
        # Try listing collections to test connection
        collections = client.get_collections()
        print("[+] Qdrant client initialized and connected successfully.")
        print(f"[+] Existing collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    # 3. Create collection if not exists
    print(f"\n[~] Checking / Creating collection '{collection_name}' (1536 dim)...")
    try:
        exists = any(c.name == collection_name for c in collections.collections)
        if not exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(
                        size=1536,
                        distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams()
                }
            )
            print(f"[+] Collection '{collection_name}' created successfully.")
        else:
            print(f"[+] Collection '{collection_name}' already exists.")
    except Exception as e:
        print(f"[-] Collection creation/check failed: {e}")
        return

    # 4. Test dummy write/read operation
    test_id = str(uuid.uuid4())
    print(f"\n[~] Testing upsert of point '{test_id}'...")
    try:
        dummy_vector = [0.1] * 1536
        dummy_sparse = SparseVector(
            indices=[42, 101],
            values=[1.0, 2.5]
        )
        metadata = {"type": "diagnostic_test", "text": "Qdrant diagnostic probe."}
        
        client.upsert(
            collection_name=collection_name,
            points=[PointStruct(
                id=test_id,
                vector={
                    "dense": dummy_vector,
                    "sparse": dummy_sparse
                },
                payload=metadata
            )]
        )
        print("[+] Upsert completed successfully.")
        
        print("\n[~] Testing query retrieval for the diagnostic point...")
        from qdrant_client.models import Prefetch, FusionQuery, Fusion
        
        response = client.query_points(
            collection_name=collection_name,
            prefetch=[
                Prefetch(
                    query=dummy_vector,
                    using="dense",
                    limit=1,
                ),
                Prefetch(
                    query=dummy_sparse,
                    using="sparse",
                    limit=1,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=1,
            with_payload=True
        )
        
        points = response.points
        if points and points[0].id == test_id:
            print(f"[+] Success! Retrieve verified (score: {points[0].score:.4f})")
            
            # Clean up the test point
            print(f"[~] Cleaning up diagnostic point '{test_id}'...")
            client.delete(
                collection_name=collection_name,
                points_selector=[test_id]
            )
            print("[+] Cleanup complete.")
            
            print("\n" + "=" * 60)
            print("[+] DIAGNOSTIC VERIFICATION PASSED SUCCESSFULLY!")
            print("    Your Qdrant integration is fully configured and operational.")
            print("=" * 60)
        else:
            print("[-] Query failed: The diagnostic point was not retrieved or ID mismatch.")
            print(f"    Points retrieved: {points}")
    except Exception as e:
        print(f"[-] Data plane read/write test failed: {e}")

if __name__ == "__main__":
    test_qdrant_connection()
