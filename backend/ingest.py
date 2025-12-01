import os
from dotenv import load_dotenv
from rich.console import Console
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SimpleField,
)
from azure.core.credentials import AzureKeyCredential

from app.config import get_settings
from app.models import DocumentChunk
from app.services.embedding_service import EmbeddingService

load_dotenv()
console = Console()
settings = get_settings()

def create_search_index():
    console.print("\n[bold cyan]creating search index...[/bold cyan]")

    index_client = SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_admin_key)
    )

    # set up vector search config
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="hnsw-config")
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )

    # define the schema
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=3072,  # text-embedding-3-large
            vector_search_profile_name="vector-profile"
        ),
        SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset)
    ]

    index = SearchIndex(
        name=settings.azure_search_index_name,
        fields=fields,
        vector_search=vector_search
    )

    try:
        # delete if exists
        try:
            index_client.delete_index(settings.azure_search_index_name)
            console.print("[yellow]deleted existing index[/yellow]")
        except:
            pass

        result = index_client.create_index(index)
        console.print(f"[green]✓[/green] created index: {result.name}")
    except Exception as e:
        console.print(f"[red]✗[/red] failed to create index: {e}")
        raise

def load_documents():
    console.print("\n[bold cyan]loading pdf documents...[/bold cyan]")

    data_dir = "./data"
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]

    if not pdf_files:
        console.print("[red]no pdf files found in ./data/[/red]")
        return []

    all_docs = []
    for pdf_file in pdf_files:
        file_path = os.path.join(data_dir, pdf_file)
        console.print(f"[yellow]→[/yellow] loading {pdf_file}...")

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        console.print(f"[green]✓[/green] loaded {len(docs)} pages from {pdf_file}")
        all_docs.extend(docs)

    console.print(f"[green]✓[/green] total pages loaded: {len(all_docs)}")
    return all_docs

def chunk_documents(documents):
    console.print("\n[bold cyan]chunking documents...[/bold cyan]")

    # split into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)

    console.print(f"[green]✓[/green] created {len(chunks)} chunks")
    return chunks

def embed_and_prepare_chunks(chunks, embedding_service):
    console.print("\n[bold cyan]generating embeddings...[/bold cyan]")

    # extract text from chunks
    texts = [chunk.page_content for chunk in chunks]

    # batch embed
    embeddings = embedding_service.generate_embeddings(texts)

    # create document chunk objects
    document_chunks = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # generate unique id
        chunk_id = f"chunk_{i}"

        # get source file and page number from metadata
        source_file = chunk.metadata.get("source", "unknown").split("/")[-1]
        page_number = chunk.metadata.get("page", None)

        doc_chunk = DocumentChunk(
            id=chunk_id,
            content=chunk.page_content,
            content_vector=embedding,
            source_file=source_file,
            page_number=page_number
        )

        document_chunks.append(doc_chunk)

    console.print(f"[green]✓[/green] prepared {len(document_chunks)} chunks with embeddings")
    return document_chunks

def upload_to_search(chunks):
    console.print("\n[bold cyan]uploading to azure search...[/bold cyan]")

    search_client = SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=AzureKeyCredential(settings.azure_search_admin_key)
    )

    # convert to dicts and exclude metadata field
    documents = [chunk.model_dump(mode='json', exclude={'metadata'}) for chunk in chunks]

    try:
        # upload in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            result = search_client.upload_documents(documents=batch)

            successes = sum(1 for r in result if r.succeeded)
            console.print(f"[green]✓[/green] uploaded batch {i//batch_size + 1}: {successes}/{len(batch)} succeeded")

        console.print(f"[green]✓[/green] upload complete!")
    except Exception as e:
        console.print(f"[red]✗[/red] upload failed: {e}")
        raise

def main():
    console.rule("[bold green]document ingestion pipeline[/bold green]")

    # step 1: create the search index
    create_search_index()

    # step 2: load pdfs
    documents = load_documents()
    if not documents:
        return

    # step 3: chunk the documents
    chunks = chunk_documents(documents)

    # step 4: generate embeddings
    embedding_service = EmbeddingService(settings)
    document_chunks = embed_and_prepare_chunks(chunks, embedding_service)

    # step 5: upload to azure search
    upload_to_search(document_chunks)

    console.rule("[bold green]✓ ingestion complete![/bold green]")
    console.print(f"\n[bold]summary:[/bold]")
    console.print(f"  • documents processed: {len(documents)} pages")
    console.print(f"  • chunks created: {len(chunks)}")
    console.print(f"  • uploaded to index: {settings.azure_search_index_name}")
    console.print(f"\n[green]ready for phase 2![/green]\n")

if __name__ == "__main__":
    main()
