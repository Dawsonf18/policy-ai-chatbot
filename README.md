# Policy AI Chatbot

A full-stack RAG (Retrieval-Augmented Generation) chatbot that helps users navigate company policy documents using natural language. Ask questions about policies and get accurate answers with source citations.

## What I Built

This project combines document ingestion, vector search, and large language models to create an intelligent chatbot that can answer questions about company policies. Instead of manually searching through PDFs, users can just ask questions in plain English and get accurate answers backed by source documents.

The system works in three phases:
1. **Document Ingestion** - Loads PDFs, chunks them into smaller pieces, generates embeddings, and stores them in Azure AI Search
2. **Backend API** - FastAPI server that handles chat requests, performs vector search, and generates responses using RAG
3. **Frontend** - Clean React interface where users can chat with the bot and see source citations

## Tech Stack

**Backend:**
- Python 3.11
- FastAPI - REST API framework
- Azure OpenAI - GPT-4 for chat, text-embedding-3-large for embeddings
- Azure AI Search - Vector database for semantic search
- LangChain - Document processing and text splitting
- Pydantic - Data validation

**Frontend:**
- React 18
- Vite - Build tool
- Vanilla CSS - Styling

## Features

- 📄 PDF document ingestion with automatic chunking
- 🔍 Semantic search using vector embeddings
- 💬 Natural language chat interface
- 📚 Source citations with page numbers and relevance scores
- ⚡ Real-time streaming responses
- 🎨 Clean, centered UI similar to modern chat apps

## Prerequisites

Before you can run this project, you'll need:

1. **Python 3.11+** installed on your machine
2. **Node.js 18+** for the frontend
3. **Azure Account** with the following services set up:
   - Azure OpenAI Service with deployments for:
     - `gpt-4o` (or `gpt-4`) for chat
     - `text-embedding-3-large` for embeddings
   - Azure AI Search service
4. **API Keys** for both services (we'll add these in the setup)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dawsonf18/policy-ai-chatbot.git
cd policy-ai-chatbot
```

### 2. Backend Setup

```bash
cd backend

# create a virtual environment
python3 -m venv venv

# activate it
source venv/bin/activate  # on windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

### 3. Configure Azure Credentials

Create a `.env` file in the `backend/` directory with your Azure credentials:

```bash
# azure openai config
AZURE_OPENAI_ENDPOINT=your-openai-endpoint
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# azure search config
AZURE_SEARCH_ENDPOINT=your-search-endpoint
AZURE_SEARCH_ADMIN_KEY=your-search-admin-key
AZURE_SEARCH_INDEX_NAME=policy-docs

# chunking settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# retrieval config
TOP_K_RESULTS=3

# llm settings
CHAT_TEMPERATURE=0.0
```

**Where to find your Azure credentials:**
- Azure Portal → Your OpenAI resource → Keys and Endpoint
- Azure Portal → Your AI Search resource → Keys

### 4. Add Your Policy Documents

Place your PDF files in the `backend/data/` directory. The project comes with an example `employee_handbook.pdf`, but you can replace it with your own policy documents.

### 5. Run the Document Ingestion

This step processes your PDFs, generates embeddings, and uploads everything to Azure AI Search:

```bash
python ingest.py
```

You should see output showing:
- PDFs being loaded
- Documents being chunked
- Embeddings being generated
- Chunks being uploaded to Azure Search

### 6. Start the Backend API

```bash
python main.py
```

The API will start on `http://localhost:8001`

### 7. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# install dependencies
npm install

# start the dev server
npm run dev
```

The frontend will start on `http://localhost:5175` (or another port if 5175 is taken)

### 8. Open in Browser

Navigate to `http://localhost:5175` and start chatting with your policy bot!

## Usage

1. Type a question about your policy documents in the chat box
2. Press Enter or click "Send"
3. The bot will search the documents and generate an answer
4. You'll see the answer along with source citations showing which documents and pages the information came from

**Example questions:**
- "How many vacation days do employees get?"
- "What is the parental leave policy?"
- "When do employees get paid?"

## Project Structure

```
policy-ai-chatbot/
├── backend/
│   ├── app/
│   │   ├── models.py              # pydantic data models
│   │   ├── config.py              # settings management
│   │   └── services/
│   │       ├── embedding_service.py   # azure openai embeddings
│   │       ├── search_service.py      # vector search
│   │       └── chat_service.py        # rag generation
│   ├── data/                      # pdf documents go here
│   ├── ingest.py                  # document ingestion script
│   ├── main.py                    # fastapi application
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # main chat interface
│   │   └── App.css                # styling
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## How It Works

1. **Document Ingestion (Phase 1)**
   - PDFs are loaded using LangChain's PyPDFLoader
   - Documents are split into 1000-character chunks with 200-character overlap
   - Each chunk is embedded using Azure OpenAI's text-embedding-3-large model
   - Chunks and embeddings are stored in Azure AI Search with metadata

2. **Query Processing (Phase 2)**
   - User question is embedded using the same embedding model
   - Vector similarity search finds the top 3 most relevant chunks
   - Retrieved chunks are passed to GPT-4 along with the question

3. **Response Generation (Phase 3)**
   - GPT-4 generates an answer using only the provided context
   - The system instructs the model to cite sources and be accurate
   - Response is returned with source documents, page numbers, and relevance scores

## Customization

**Change the number of results retrieved:**
Update `TOP_K_RESULTS` in your `.env` file (default is 3)

**Adjust chunk size:**
Modify `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`

**Use a different model:**
Change `AZURE_OPENAI_CHAT_DEPLOYMENT` to use GPT-3.5, GPT-4, or other models

**Customize the system prompt:**
Edit the system prompt in `backend/app/services/chat_service.py`

## Troubleshooting

**"Address already in use" error:**
Another process is using the port. Kill it with:
```bash
lsof -ti:8001 | xargs kill -9  # backend
lsof -ti:5175 | xargs kill -9  # frontend
```

**"No module named 'app'" error:**
Make sure you're in the backend directory and your virtual environment is activated.

**"The given API key doesn't match" error:**
Double-check your Azure credentials in the `.env` file.

**Frontend won't start:**
If you have Node.js version issues, the project uses Vite 4 which supports Node 18+.

## Future Improvements

- Add conversation history to maintain context across multiple questions
- Support more document formats (Word, Excel, etc.)
- Add user authentication
- Deploy to Azure App Service or AWS
- Add a "reset conversation" button
- Implement streaming responses for real-time feedback

## License

MIT License - feel free to use this project however you'd like!

## Questions?

If you run into issues or have questions, feel free to open an issue on GitHub.
