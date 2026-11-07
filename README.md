# Enterprise RAG Document Assistant

An enterprise-style **Retrieval-Augmented Generation (RAG)** application that allows authenticated users to upload internal documents and ask natural-language questions grounded in those documents.

The system combines **FastAPI, React, PostgreSQL, pgvector, Ollama, semantic search, hybrid retrieval, reranking, and source citations**.

---

## Overview

The goal of this project is to demonstrate how an enterprise AI knowledge assistant can securely answer questions from internal documents.

Users can:

- Register and login securely
- Upload PDF, DOCX, and TXT documents
- Extract and store document text
- Split documents into page-aware chunks
- Generate semantic embeddings
- Store embeddings using PostgreSQL + pgvector
- Ask questions in natural language
- Retrieve relevant document chunks
- Filter retrieval by document
- Use hybrid keyword + vector retrieval
- Rerank retrieved chunks
- Generate grounded answers using Ollama
- View source document and page citations
- Maintain conversation history

---

# Architecture

```text
React Frontend
      |
      v
FastAPI REST API
      |
      +----------------------+
      |                      |
      v                      v
Authentication          Document Service
JWT + Argon2                 |
                             v
                     Text Extraction
                             |
                             v
                     Page-aware Chunking
                             |
                             v
                    Ollama Embeddings
                             |
                             v
                   PostgreSQL + pgvector
                             |
                             v
                        RAG Service
                             |
            +----------------+----------------+
            |                                 |
            v                                 v
     Vector Retrieval                  Keyword Retrieval
            |                                 |
            +---------------+-----------------+
                            |
                            v
                       Reranking
                            |
                            v
                    Context Construction
                            |
                            v
                       Ollama LLM
                            |
                            v
                   Grounded Answer
                            |
                            v
                Source + Page Citations
```

---

# RAG Flow

## Document ingestion

```text
Upload Document
      ↓
Validate File
      ↓
Save File
      ↓
Extract Text
      ↓
Split by Page
      ↓
Chunk Text
      ↓
Generate Embeddings
      ↓
Store Chunks + Embeddings
      ↓
PostgreSQL + pgvector
```

## Question answering

```text
User Question
      ↓
Generate Query Embedding
      ↓
Vector Similarity Search
      +
Keyword Search
      ↓
Combine Results
      ↓
Rerank Results
      ↓
Select Top-K Chunks
      ↓
Build RAG Context
      ↓
Ollama LLM
      ↓
Grounded Answer
      ↓
Document + Page Citations
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Alembic
- Pydantic
- PyJWT
- Argon2
- httpx

## AI / RAG

- Ollama
- `nomic-embed-text`
- `llama3.2:3b`
- pgvector
- sentence-transformers CrossEncoder
- Semantic search
- Keyword retrieval
- Reranking

## Frontend

- React
- Vite
- Fetch API
- Server-Sent Events

---

# Key Features

## Authentication

- User registration
- User login
- JWT access tokens
- Argon2 password hashing
- Protected APIs
- Current-user resolution

---

## AI Chat

- Persistent conversations
- Conversation history
- Message storage
- SSE-based responses
- LLM provider abstraction

---

## Document Management

Supported file types:

```text
PDF
DOCX
TXT
```

Features:

- Secure document upload
- File type validation
- Maximum file size validation
- UUID-based storage filenames
- Text extraction
- Page count
- Processing status
- Document listing
- Document deletion
- Ownership validation

---

## Core RAG

Documents are converted into chunks before retrieval.

Current chunking configuration:

```text
Chunk Size: 1000 characters
Chunk Overlap: 200 characters
```

Each chunk contains:

```text
document_id
chunk_index
page_number
content
embedding
```

---

# Embeddings

The project currently uses Ollama:

```text
nomic-embed-text
```

Embedding dimension:

```text
768
```

Embeddings are stored using:

```text
PostgreSQL + pgvector
```

Example:

```text
Document Chunk
      ↓
Ollama Embedding Model
      ↓
768-dimensional vector
      ↓
pgvector
```

---

# Semantic Search

User questions are converted into embeddings using the same embedding model.

pgvector performs cosine similarity search:

```text
Question
    ↓
Query Embedding
    ↓
Compare against Document Chunk Embeddings
    ↓
Top-K Relevant Chunks
```

---

# Hybrid Retrieval

The project combines:

```text
Semantic Vector Search
+
Keyword Search
```

Vector search helps understand semantic meaning.

Keyword search helps locate exact words or phrases.

The results are combined and deduplicated before reranking.

---

# Reranking

Retrieved chunks are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Flow:

```text
Vector + Keyword Results
        ↓
CrossEncoder
        ↓
Relevance Scores
        ↓
Best Top-K Chunks
```

This improves the quality of the context passed to the LLM.

---

# Secure Retrieval

Retrieval is restricted by the authenticated user.

```text
User A
→ searches only User A's documents

User B
→ cannot retrieve User A's document chunks
```

The query filters using:

```text
documents.owner_id = current_user.id
```

This is important for enterprise data isolation.

---

# Document Filtering

Users can choose:

```text
All Documents
```

or:

```text
Specific Document
```

When a document is selected, retrieval searches only chunks belonging to that document.

---

# Source Citations

Answers include source metadata.

Example:

```text
Answer:
The warranty period is 24 months from the original purchase date.

Sources:
enterprise_rag_large_test_document.pdf - Page 4
manual.pdf - Page 1
```

For PDF documents, page-aware chunking enables page citations.

---

# Grounded Answering

The LLM is instructed to answer only from retrieved document context.

If relevant information is unavailable:

```text
I could not find the answer in the uploaded documents.
```

This reduces hallucination and keeps answers document-grounded.

---

# Ollama

Ollama is used for local AI inference.

Current models:

```text
Embeddings:
nomic-embed-text

LLM:
llama3.2:3b
```

Benefits:

- Local execution
- No API usage cost
- Better data privacy
- Offline development
- Easy model switching

The architecture keeps providers loosely coupled so OpenAI or Azure OpenAI can be added later.

---

# Provider Architecture

## LLM

```text
LLMProvider
├── MockLLMProvider
├── OllamaLLMProvider
└── OpenAIProvider
```

## Embeddings

```text
EmbeddingProvider
├── MockEmbeddingProvider
├── OllamaEmbeddingProvider
└── OpenAIEmbeddingProvider
```

This keeps the application independent from a single AI provider.

---

# Project Structure

```text
enterprise-rag-document-assistant/
│
├── backend/
│   ├── alembic/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── routers/
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── dependencies/
│   │   ├── embeddings/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Login.jsx
│   │   ├── Chat.jsx
│   │   ├── Documents.jsx
│   │   └── api.js
│   │
│   └── package.json
│
└── README.md
```

---

# Backend Architecture

The backend follows:

```text
Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

Example:

```text
DocumentsRouter
      ↓
DocumentService
      ↓
DocumentRepository
      ↓
SQLAlchemy
      ↓
PostgreSQL
```

This separates:

- HTTP handling
- Business logic
- Database operations

---

# Database Entities

Main tables:

```text
users
conversations
messages
documents
document_chunks
```

Relationships:

```text
User
 ├── Conversations
 │      └── Messages
 │
 └── Documents
        └── DocumentChunks
```

---

# Version History

## V1 — Foundation + Authentication

Implemented:

- FastAPI project structure
- PostgreSQL
- SQLAlchemy
- Alembic
- User model
- Registration
- Login
- JWT authentication
- Argon2 password hashing
- Protected APIs
- React login

Tag:

```text
v1.0.0
```

---

## V2 — AI Chat Platform

Implemented:

- Conversations
- Messages
- Chat API
- Conversation history
- LLM provider abstraction
- OpenAI provider
- Mock provider
- SSE-based chat
- React chat UI

Tag:

```text
v2.0.0
```

---

## V3 — Document Management

Implemented:

- PDF/DOCX/TXT upload
- File validation
- File storage
- Text extraction
- Processing status
- Document list
- Document details
- Document deletion
- Ownership checks
- React document management

Tag:

```text
v3.0.0
```

---

## V4 — Core RAG

Implemented:

- Document chunks
- Chunk overlap
- pgvector
- Ollama embeddings
- Semantic similarity search
- Top-K retrieval
- RAG prompt construction
- Ollama LLM
- Grounded answers
- Safe fallback
- Secure retrieval

Tag:

```text
v4.0.0
```

---

## V5 — Advanced RAG

Implemented:

- Page-aware chunking
- Page citations
- Multi-document retrieval
- Document filtering
- Vector + keyword hybrid retrieval
- CrossEncoder reranking
- Source metadata
- User-level secure retrieval

Tag:

```text
v5.0.0
```

---

# Roadmap

## V6 — Reliability + Evaluation

Planned:

- Pytest
- Mock provider tests
- RAG retrieval tests
- Retry / timeout handling
- Rate limiting
- Structured exceptions
- Token usage tracking
- Recall@K
- Precision@K
- Faithfulness evaluation
- Answer relevance evaluation

---

## V7 — Deployment + Observability

Planned:

- Docker
- Docker Compose
- PostgreSQL + pgvector container
- Backend container
- Frontend container
- GitHub Actions
- Structured logging
- Request IDs
- Health checks
- Readiness checks
- Azure deployment

---

# Local Setup

## 1. Clone repository

```bash
git clone https://github.com/girishdev/enterprise-rag-document-assistant.git

cd enterprise-rag-document-assistant
```

---

## 2. Backend setup

```bash
cd backend

python -m venv .venv
```

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# PostgreSQL

Create a PostgreSQL database and configure:

```text
DATABASE_URL
```

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Run migrations:

```bash
alembic upgrade head
```

---

# Ollama Setup

Install Ollama and pull embedding model:

```bash
ollama pull nomic-embed-text
```

Pull LLM:

```bash
ollama pull llama3.2:3b
```

Verify:

```bash
ollama list
```

Expected:

```text
nomic-embed-text
llama3.2:3b
```

Ollama normally runs locally at:

```text
http://localhost:11434
```

---

# Run Backend

```bash
cd backend
source .venv/Scripts/activate

uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Frontend API configuration:

```text
VITE_API_URL=http://localhost:8000/api/v1
```

---

# Example Questions

After uploading test documents:

```text
What is the warranty period?

When should preventive maintenance be performed?

How does vector search work?

How many annual leave days are provided?

How many sick leave days are allowed?

What should be included in a support request?
```

Unrelated question:

```text
Who won the FIFA World Cup?
```

Expected:

```text
I could not find the answer in the uploaded documents.
```

---

# Security Considerations

Implemented:

- Password hashing using Argon2
- JWT authentication
- Protected APIs
- Conversation ownership checks
- Document ownership checks
- User-filtered retrieval
- No cross-user document retrieval
- UUID-based stored filenames

---

# Current Limitations

- OCR for scanned/image-only PDFs is not implemented
- DOCX and TXT do not provide reliable page citations
- Files currently use local filesystem storage
- Ollama must be installed locally
- Background document processing is not yet implemented
- Retrieval evaluation will be added in V6
- Production deployment will be added in V7

---

# Design Decisions

## Why PostgreSQL + pgvector?

Using pgvector keeps:

```text
Users
Documents
Metadata
Permissions
Embeddings
```

inside the same database.

This simplifies secure metadata filtering and enterprise-style retrieval.

---

## Why Ollama?

Ollama provides:

- local LLM execution
- local embedding generation
- privacy-friendly development
- no API cost during development
- easy model experimentation

The provider abstraction allows switching to cloud services later.

---

## Why Hybrid Retrieval?

Vector search is strong for semantic meaning.

Keyword search is strong for exact terms.

Combining both improves retrieval coverage.

---

## Why Reranking?

Initial retrieval may return several partially relevant chunks.

A CrossEncoder evaluates:

```text
Question + Retrieved Chunk
```

together and reorders them based on relevance before they are sent to the LLM.

---

# Interview Talking Points

This project demonstrates:

- Clean FastAPI backend architecture
- REST API design
- JWT authentication
- Repository and service patterns
- PostgreSQL and SQLAlchemy
- Database migrations
- File processing
- Async Python
- LLM abstraction
- Local LLM integration
- Embeddings
- Vector databases
- Semantic search
- RAG architecture
- Secure retrieval
- Multi-document search
- Metadata filtering
- Hybrid retrieval
- Reranking
- Grounded generation
- Source citations

---

# Purpose

This project was built as a practical demonstration of:

> **Backend Engineering + Enterprise AI + Retrieval-Augmented Generation**

with an emphasis on secure, maintainable, provider-independent architecture.