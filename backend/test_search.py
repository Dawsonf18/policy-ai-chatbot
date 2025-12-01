from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from app.config import get_settings

settings = get_settings()

# connect to search
client = SearchClient(
    endpoint=settings.azure_search_endpoint,
    index_name=settings.azure_search_index_name,
    credential=AzureKeyCredential(settings.azure_search_admin_key)
)

print("\n=== testing phase 1 ingestion ===\n")

# check total documents
results = client.search("*", top=1, include_total_count=True)
total = results.get_count()
print(f"✓ total documents indexed: {total}")

# try a search
print("\n--- searching for 'vacation' ---\n")
results = client.search("vacation", top=3)

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc['source_file']} (page {doc.get('page_number', 'N/A')})")
    print(f"   {doc['content'][:150]}...")
    print()

print("✓ phase 1 is working!\n")
