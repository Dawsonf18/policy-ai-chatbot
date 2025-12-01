from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import ChatRequest, ChatResponse
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.services.chat_service import ChatService

# initialize settings
settings = get_settings()

# create fastapi app
app = FastAPI(
    title="Policy Chatbot API",
    description="RAG-based chatbot for company policies",
    version="1.0.0"
)

# cors middleware - allow frontend to call the api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, specify your frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize services
embedding_service = EmbeddingService(settings)
search_service = SearchService(settings, embedding_service)
chat_service = ChatService(settings)

@app.get("/")
def read_root():
    return {
        "message": "policy chatbot api",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # step 1: search for relevant documents
        sources = search_service.search_documents(request.question)

        if not sources:
            raise HTTPException(
                status_code=404,
                detail="no relevant documents found for your question"
            )

        # step 2: generate answer using rag
        response = chat_service.generate_answer(request.question, sources)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
