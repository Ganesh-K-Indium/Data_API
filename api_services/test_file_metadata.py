"""
Test script to inspect file metadata structure
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.sharepoint_utils import SharePointUtils

def test_file_metadata():
    """Test what metadata is actually available for files"""
    print("=" * 60)
    print("SharePoint File Metadata Test")
    print("=" * 60)
    
    try:
        # Get SharePoint client
        print("\n1. Connecting to SharePoint...")
        client = SharePointUtils()
        print(f"   ✓ Connected to: {client.site_url}")
        
        # List files
        print("\n2. Listing files from Documents library...")
        files = client.list_files(library_name="Documents")
        print(f"   ✓ Found {len(files)} files")
        
        if not files:
            print("   ⚠️  No files found")
            return
        
        # Inspect first file in detail
        print("\n3. Detailed inspection of first file:")
        print("-" * 60)
        
        test_file = files[0]
        print(f"\nFile: {test_file.get('name', 'Unknown')}")
        print(f"\nAll keys: {list(test_file.keys())}")
        print("\nKey-Value pairs:")
        
        for key, value in test_file.items():
            if key == 'downloadUrl':
                # Show first 80 chars of download URL
                if value:
                    print(f"  {key}: {value[:80]}...")
                else:
                    print(f"  {key}: (empty)")
            elif isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
        
        # Test JSON serialization
        print("\n4. Testing JSON serialization (as frontend does):")
        print("-" * 60)
        file_json = json.dumps(test_file)
        print(f"\nJSON length: {len(file_json)} characters")
        print(f"First 200 chars: {file_json[:200]}...")
        
        # Test JSON deserialization
        print("\n5. Testing JSON deserialization (as backend does):")
        print("-" * 60)
        parsed = json.loads(file_json)
        print(f"\nKeys after parse: {list(parsed.keys())}")
        print(f"Has downloadUrl: {'downloadUrl' in parsed}")
        
        if 'downloadUrl' in parsed:
            print(f"downloadUrl exists: {parsed['downloadUrl'][:80]}...")
        else:
            print("⚠️  downloadUrl NOT found after parsing!")
        
        # Test with metadata nested
        print("\n6. Checking if metadata is nested:")
        print("-" * 60)
        if 'metadata' in test_file:
            print(f"'metadata' key exists!")
            print(f"Type: {type(test_file['metadata'])}")
            print(f"Value: {test_file['metadata']}")
            
            # Check if downloadUrl is in metadata
            if isinstance(test_file['metadata'], dict):
                print(f"Metadata keys: {list(test_file['metadata'].keys())}")
        else:
            print("No 'metadata' key found")
        
        # Show what would be sent to ingestion
        print("\n7. Simulating ingestion payload:")
        print("-" * 60)
        
        # This is what the frontend should send
        ingestion_payload = [json.dumps(f) for f in files[:2]]
        print(f"Number of files: {len(ingestion_payload)}")
        print(f"\nFirst file payload (first 300 chars):")
        print(ingestion_payload[0][:300])
        
        # Parse it back like backend does
        print("\n8. Backend parsing simulation:")
        print("-" * 60)
        file_id = ingestion_payload[0]
        if isinstance(file_id, str) and file_id.startswith('{'):
            parsed_data = json.loads(file_id)
            print(f"Parsed keys: {list(parsed_data.keys())}")
            print(f"Has downloadUrl: {'downloadUrl' in parsed_data}")
            
            if 'downloadUrl' in parsed_data:
                print(f"✓ downloadUrl found: {parsed_data['downloadUrl'][:80]}...")
            else:
                print("✗ downloadUrl NOT found!")
                print("\nAvailable keys and their types:")
                for key in parsed_data.keys():
                    val = parsed_data[key]
                    print(f"  {key}: {type(val).__name__}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_metadata()
