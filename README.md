# Production-Grade Multi-Engine Agentic AI System

A modular, production-ready AI system built with FastAPI and Docker that demonstrates agentic workflows, autonomous tool usage, semantic caching, reflection-based self-improvement, and cloud deployment on AWS.

This project is designed to showcase deep understanding of:
-Agent orchestration
-Multi-engine architecture
-Autonomous tool execution
-Reflection loops
-Semantic knowledge bases
-Structured logging
-Reverse proxy and cloud deployment

# 🚀 Overview
This system routes user input through an LLM-based intent resolver and dynamically selects the appropriate execution engine:

💬 Chat engine (context-aware conversation)
🔎 Lookup engine (real-time factual retrieval)
🧠 Deep analysis engine (structured reasoning)
🤖 Autonomous engine (multi-step tool-driven reasoning)

Each engine operates independently under a standardized contract and may use:
-Tool registry (search, calculator, reasoning)
-Reflection memory (self-critique + retry)
-Semantic knowledge base (vector-based caching)

The system is containerized and deployed to AWS using Docker, Nginx reverse proxy, and EC2.

# 🏗 High-Level Architecture
<img width="1070" height="557" alt="image" src="https://github.com/user-attachments/assets/44945f58-9bb0-4ddb-9b04-4cb8f5347b08" />

# Autonomous Execution Loop
<img width="310" height="678" alt="image" src="https://github.com/user-attachments/assets/52737089-db81-4b8c-be99-7e5aa311cdad" />

# The autonomous engine:
-Decides next action using LLM reasoning.
-Executes selected tool.
-Reflects on output quality.
-Retries if confidence is low.
-Returns final answer with confidence score.

# ⚙️ Core Components

# 1️⃣ Controller Layer
Handles:
-Request lifecycle
-Structured logging
-Intent routing
-Knowledge base lookup
-Engine selection
-Response assembly

No business logic lives here.

# 2️⃣ Intent Resolver
LLM-based classifier that determines:
-chat
-lookup
-deep_analysis
-autonomous

It also rewrites context-dependent questions into standalone tasks.

# 3️⃣ Engine Layer
All engines implement:
run(task: str, context: ExecutionContext) -> EngineResult

# Where EngineResult includes:
-final_output
-confidence_score
-metadata (optional)

# Chat Engine
Lightweight conversational responses using short-term memory.

# Lookup Engine
Uses search tool for time-sensitive or factual queries.

# Deep Analysis Engine
Structured multi-step reasoning with reflection loop.

# Autonomous Engine
Self-directed planning with tool selection and critique-based retries.

# 4️⃣ Tool Registry
Tools are registered once at startup and injected into engines.

Examples:
-search_web
-calculate
-llm_reason
-embeddings

Each tool is stateless and isolated.

# 5️⃣ Memory Systems

# Conversation Memory
Maintains short-term conversational state.

# Knowledge Base
Vector-based semantic cache that:
-Stores high-confidence answers
-Retrieves similar queries
-Reduces redundant LLM calls

# Reflection Memory
-Stores low-confidence critiques and weaknesses.
-Used to improve future similar tasks.

# 6️⃣ Structured Logging

All requests are logged in JSON format:
{
  "timestamp": "...",
  "request_id": "...",
  "intent": "autonomous",
  "engine": "AutonomousEngine",
  "confidence_score": 8,
  "latency_ms": 1432
}

Designed for:
-CloudWatch
-Observability
-Production monitoring

# 🐳 Deployment Architecture

Current deployment:
<img width="589" height="360" alt="image" src="https://github.com/user-attachments/assets/819900e7-0035-4dfc-ab2f-1a7497983d6a" />

Infrastructure:
-AWS EC2
-Docker container
-Nginx reverse proxy
-Port 8000 bound to localhost
-Port 80 publicly exposed
-Auto-restart via Docker restart policy

# 🛠 Tech Stack
-Python 3.12
-FastAPI
-OpenAI API
-NumPy (vector similarity)
-Docker
-Nginx
-AWS EC2
-Structured JSON logging

Docker

Nginx

AWS EC2

Structured JSON logging

# 🧪 Example Capabilities
-Conversational
Explain local LLM like I’m 5.

-Lookup
Who is the current prime minister of Japan?

-Deep Analysis
Compare Nvidia vs AMD for AI training workloads.

-Autonomous Planning
Design a 6-month marathon training plan for a 10K runner.

# 🚀 Local Development
docker build -t analyst-agent-chat .
docker run -p 8000:8000 --env-file .env analyst-agent-chat

Health check:
http://localhost:8000/health

# ☁️ AWS Deployment (EC2)
-Launch Ubuntu EC2 instance
-Install Docker + Nginx
-Bind container to 127.0.0.1:8000
-Configure Nginx reverse proxy
-Open port 80 in security group
-Enable restart policy

# 📈 Future Improvements
-Move to ECS + Fargate
-Add HTTPS with ALB
-Replace JSON storage with SQLite or Postgres
-Add metrics dashboard
-Add rate limiting & auth layer
-Add tool cost accounting

# 📌 Project Intent
This project was built to explore:
-Agentic AI workflows
-Modular system design
-Cloud-native deployment patterns
-Production-oriented backend architecture
-It emphasizes system design, robustness, and observability over UI polish.

# 👨‍💻 Author
Built and deployed by Hemant Gupta.
