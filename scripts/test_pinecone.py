import sys
import os
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import settings
from pinecone import Pinecone, ServerlessSpec

def test_pinecone_connection():
    print("=" * 60)
    print("PINECONE VECTOR DATABASE DIAGNOSTIC UTILITY")
    print("=" * 60)
    
    # 1. Check Configuration
    print(f"[+] Loaded .env file: {os.path.exists('.env')}")
    api_key = settings.pinecone.api_key or os.environ.get("PINECONE_API_KEY")
    index_name = settings.pinecone.index_name or os.environ.get("PINECONE_INDEX_NAME") or "nova-policies"
    environment = settings.pinecone.environment or os.environ.get("PINECONE_ENVIRONMENT") or "us-east-1"
    
    if not api_key or api_key == "your_pinecone_api_key_here":
        print("[-] Error: PINECONE_API_KEY is missing or contains the default placeholder!")
        print("    Please configure a valid Pinecone key in your .env file.")
        return
        
    print(f"[+] API Key detected: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}")
    print(f"[+] Target Index: {index_name}")
    print(f"[+] Region environment: {environment}")
    
    # 2. Initialize client
    print("\n[~] Connecting to Pinecone...")
    try:
        pc = Pinecone(api_key=api_key)
        print("[+] Pinecone client initialized successfully.")
    except Exception as e:
        print(f"[-] Client initialization failed: {e}")
        return

    # 3. Test Control Plane (List Indexes)
    print("\n[~] Retrieving indexes list (Control Plane)...")
    control_plane_working = False
    try:
        indexes = pc.list_indexes()
        existing_names = [idx.name for idx in indexes]
        print(f"[+] Connection active. Existing indexes: {existing_names}")
        control_plane_working = True
    except Exception as e:
        print(f"[!] Warning: Control plane list_indexes() failed: {e}")
        print("    This is common if your API key has restricted data-plane-only permissions.")
        print("    We will attempt to connect to the index directly.")
        existing_names = []

    # 4. Check / Create index
    if control_plane_working:
        if index_name not in existing_names:
            print(f"\n[~] Creating serverless index '{index_name}' (1536 dim)...")
            try:
                pc.create_index(
                    name=index_name,
                    dimension=1536,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=environment
                    )
                )
                print(f"[+] Index '{index_name}' created successfully.")
            except Exception as e:
                print(f"[-] Index creation failed: {e}")
                return
        else:
            print(f"[+] Index '{index_name}' is confirmed present.")

    # 5. Test Data Plane Operations (Index Stats, Upsert, Query)
    print(f"\n[~] Connecting to index '{index_name}' (Data Plane)...")
    try:
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"[+] Connection successful.")
        print(f"[+] Index Stats: Total vectors = {stats.get('total_vector_count', 0)}")
        print(f"[+] Index namespaces: {stats.get('namespaces', {})}")
    except Exception as e:
        print(f"[-] Connection to index '{index_name}' failed: {e}")
        print("    Please verify the index exists in your Pinecone dashboard and is active.")
        return

    # 6. Test dummy write/read operation
    test_id = f"diagnostic-test-{uuid.uuid4()}"
    print(f"\n[~] Testing upsert of point '{test_id}'...")
    try:
        # Dummy 1536 dimension vector
        dummy_vector = [0.1] * 1536
        dummy_sparse = {
            "indices": [42, 101],
            "values": [1.0, 2.5]
        }
        metadata = {"type": "diagnostic_test", "text": "Pinecone diagnostic probe."}
        
        index.upsert(vectors=[{
            "id": test_id,
            "values": dummy_vector,
            "sparse_values": dummy_sparse,
            "metadata": metadata
        }])
        print("[+] Upsert completed successfully.")
        
        print("\n[~] Testing query retrieval for the diagnostic point...")
        query_response = index.query(
            vector=dummy_vector,
            sparse_vector=dummy_sparse,
            top_k=1,
            include_metadata=True
        )
        
        matches = query_response.get("matches", [])
        if matches and matches[0]["id"] == test_id:
            print(f"[+] Success! Retrieve verified (score: {matches[0].get('score'):.4f})")
            
            # Clean up the test point
            print(f"[~] Cleaning up diagnostic point '{test_id}'...")
            index.delete(ids=[test_id])
            print("[+] Cleanup complete.")
            
            print("\n" + "=" * 60)
            print("[+] DIAGNOSTIC VERIFICATION PASSED SUCCESSFULLY!")
            print("    Your Pinecone integration is fully configured and operational.")
            print("=" * 60)
        else:
            print("[-] Query failed: The diagnostic point was not retrieved or ID mismatch.")
            print(f"    Matches retrieved: {matches}")
    except Exception as e:
        print(f"[-] Data plane read/write test failed: {e}")

if __name__ == "__main__":
    test_pinecone_connection()
