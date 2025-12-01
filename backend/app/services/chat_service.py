from typing import List
from openai import AzureOpenAI

from app.config import Settings
from app.models import SourceDocument, ChatResponse

class ChatService:
    def __init__(self, settings: Settings):
        self.settings = settings

        # initialize azure openai client
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )

    def generate_answer(self, question: str, sources: List[SourceDocument]) -> ChatResponse:
        # build context from retrieved documents
        context = "\n\n".join([
            f"[Source: {src.source_file}, Page: {src.page_number}]\n{src.content_snippet}"
            for src in sources
        ])

        # system prompt for the rag chatbot
        system_prompt = """you are a helpful assistant that answers questions about company policies.
use only the provided context to answer questions. if you can't find the answer in the context,
say you don't know. be concise and accurate."""

        # user prompt with context
        user_prompt = f"""context from company policy documents:

{context}

question: {question}

answer based only on the context above:"""

        # call azure openai
        response = self.client.chat.completions.create(
            model=self.settings.azure_openai_chat_deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.settings.chat_temperature
        )

        answer = response.choices[0].message.content

        return ChatResponse(
            answer=answer,
            sources=sources
        )
