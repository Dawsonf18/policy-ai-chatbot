from typing import List
from openai import AzureOpenAI
from rich.console import Console

from app.config import Settings

console = Console()

class EmbeddingService:
    def __init__(self, settings: Settings):
        self.settings = settings

        # initialize the azure openai client
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )

        console.print(
            f"[green]✓[/green] embedding service ready with {settings.azure_openai_embedding_deployment}"
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        # batch process for efficiency
        console.print(f"[yellow]→[/yellow] generating embeddings for {len(texts)} chunks...")

        response = self.client.embeddings.create(
            input=texts,
            model=self.settings.azure_openai_embedding_deployment
        )

        embeddings = [item.embedding for item in response.data]

        console.print(
            f"[green]✓[/green] got {len(embeddings)} embeddings (dimension: {len(embeddings[0])})"
        )

        return embeddings

    def generate_single_embedding(self, text: str) -> List[float]:
        # for single text like user questions
        response = self.client.embeddings.create(
            input=[text],
            model=self.settings.azure_openai_embedding_deployment
        )

        return response.data[0].embedding
