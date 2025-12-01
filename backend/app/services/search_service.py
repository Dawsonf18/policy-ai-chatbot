from typing import List
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from app.config import Settings
from app.models import SourceDocument
from app.services.embedding_service import EmbeddingService

class SearchService:
    def __init__(self, settings: Settings, embedding_service: EmbeddingService):
        self.settings = settings
        self.embedding_service = embedding_service

        # connect to azure search
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_admin_key)
        )

    def search_documents(self, question: str) -> List[SourceDocument]:
        # generate embedding for the question
        question_vector = self.embedding_service.generate_single_embedding(question)

        # do vector search
        results = self.client.search(
            search_text=None,  # pure vector search
            vector_queries=[{
                "kind": "vector",
                "vector": question_vector,
                "fields": "content_vector",
                "k": self.settings.top_k_results
            }]
        )

        # convert to source documents
        sources = []
        for result in results:
            source = SourceDocument(
                source_file=result["source_file"],
                page_number=result.get("page_number"),
                content_snippet=result["content"],
                relevance_score=result["@search.score"]
            )
            sources.append(source)

        return sources
