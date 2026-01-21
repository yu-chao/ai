# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PlantMate Agents is a flexible, extensible multi-agent framework built on OpenAI's native API. It provides agent development patterns, tool systems, memory management, RAG capabilities, protocol support (MCP, A2A, ANP), evaluation frameworks, and RL training.

## Development Commands

### Installation
```bash
# Core installation
pip install -e .

# With optional dependencies (extras)
pip install -e ".[search]"      # Search functionality (Tavily, SerpApi)
pip install -e ".[memory]"      # Memory system (Qdrant, Neo4j, spaCy)
pip install -e ".[rag]"         # RAG system (scikit-learn, transformers, torch)
pip install -e ".[protocols]"   # Protocol support (fastmcp, a2a-sdk)
pip install -e ".[evaluation]"  # Evaluation system
pip install -e ".[rl]"          # RL training system
pip install -e ".[all]"         # Everything
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v --tb=short
```

### Code Quality
```bash
# Format code with Black
black plantmate_agents/

# Sort imports with isort
isort plantmate_agents/

# Type checking with mypy
mypy plantmate_agents/
```

### Running the FastAPI Server
```bash
# Development server (with auto-reload)
python -m server.app

# Or using uvicorn directly
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the API
```bash
# Run API tests
python test_api.py
```

## Architecture

### Core Components (`plantmate_agents/core/`)

- **`HelloAgentsLLM`** (llm.py): Unified LLM client supporting multiple providers (OpenAI, DeepSeek, Qwen, ModelScope, Kimi, Zhipu, Ollama, vLLM). Auto-detects provider from environment variables or parameters. Uses streaming by default via `think()` method.
- **`Config`** (config.py): Configuration management using Pydantic models
- **`Message`** (message.py): Message data structure for conversation history
- **`Agent`** (agent.py): Abstract base class for all agent implementations

### Agent Patterns (`plantmate_agents/agents/`)

All agents extend the base `Agent` class:

- **`SimpleAgent`**: Basic conversational agent with optional tool calling. Parses tool calls from text using `[TOOL_CALL:tool_name:params]` format. Supports multi-step tool iteration.
- **`FunctionCallAgent`**: Uses OpenAI's native function calling
- **`ReActAgent`**: Reasoning + Acting pattern with thought/action/observation loop
- **`ReflectionAgent`**: Self-reflection before final response
- **`PlanAndSolveAgent`**: Planning first, then execution
- **`ToolAwareSimpleAgent`**: Tool-aware variant of SimpleAgent

### Tool System (`plantmate_agents/tools/`)

- **`Tool` (base.py)**: Abstract base class with `expandable` flag. Tools can expand into multiple sub-tools using `@tool_action` decorator. Supports OpenAI function calling schema conversion.
- **`ToolRegistry` (registry.py)**: Manages tool registration and execution. Auto-expands expandable tools by default.
- **Built-in tools** (builtin/): SearchTool, CalculatorTool, MemoryTool, RAGTool, NoteTool, TerminalTool, protocol tools (MCP/A2A/ANP), evaluation tools

### Memory System (`plantmate_agents/memory/`)

- **`MemoryManager` (manager.py)**: Unified interface for all memory types. Handles memory lifecycle, importance scoring, forgetting, consolidation between types.
- **Memory types** (types/):
  - `WorkingMemory`: Short-term, limited capacity
  - `EpisodicMemory`: Event-based experiences with Qdrant vector storage
  - `SemanticMemory`: Factual knowledge with Neo4j graph storage
  - `PerceptualMemory`: Multi-modal sensory data
- **Storage backends** (storage/): Qdrant (vectors), Neo4j (graphs)
- **RAG pipeline** (rag/): Document processing, chunking, embedding, retrieval

### Protocol Support (`plantmate_agents/protocols/`)

- **MCP** (mcp/): Model Context Protocol - requires `fastmcp`
- **A2A** (a2a/): Agent-to-Agent communication protocol
- **ANP** (anp/): Agent Network Protocol for service discovery

### Evaluation (`plantmate_agents/evaluation/`)

Benchmark evaluation frameworks including BFCL, GAIA, LLM Judge, and Win Rate metrics.

### RL Training (`plantmate_agents/rl/`)

Reinforcement learning training system using TRL library for agent fine-tuning.

## Environment Configuration

Copy `.env.example` to `.env` and configure:

### LLM Configuration (Unified Format)
The framework auto-detects provider from these variables:
```
LLM_MODEL_ID=your-model-name
LLM_API_KEY=your-api-key
LLM_BASE_URL=your-api-base-url
LLM_TIMEOUT=60
```

Or use provider-specific variables (e.g., `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`).

### Database Configuration
- **Qdrant** (vector store): `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`
- **Neo4j** (graph store): `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`

### Search Tools
- **Tavily**: `TAVILY_API_KEY`
- **SerpApi**: `SERPAPI_API_KEY`

### Other
- **Embedding**: `EMBED_MODEL_TYPE`, `EMBED_MODEL_NAME`, `EMBED_API_KEY`
- **GitHub**: `GITHUB_PERSONAL_ACCESS_TOKEN`
- **HuggingFace**: `HF_TOKEN`

## Key Design Patterns

### Tool Creation
```python
from plantmate_agents.tools import Tool, ToolParameter, tool_action

class MyTool(Tool, expandable=True):
    def __init__(self):
        super().__init__(name="my_tool", description="...", expandable=True)

    @tool_action("my_action", "Does something")
    def _my_action(self, param: str, count: int = 1) -> str:
        '''Action description

        Args:
            param: Parameter description
            count: Count description
        '''
        return "result"
```

### Agent Usage
```python
from plantmate_agents import HelloAgentsLLM, SimpleAgent

llm = HelloAgentsLLM()  # Auto-detects from env
agent = SimpleAgent(name="assistant", llm=llm, system_prompt="...")
response = agent.run("user input")
```

### Memory Integration
```python
from plantmate_agents.memory import MemoryManager

memory = MemoryManager(user_id="user123")
memory.add_memory("content", memory_type="episodic", importance=0.8)
results = memory.retrieve_memories("query", limit=5)
```

## Important Notes

- **Python 3.10+ is required**
- **BFCL evaluation** requires `numpy==1.26.4` which conflicts with core `numpy>=2.0` - must use separate venv
- **Qdrant client**: Version pinned to `<1.16.0` due to removed `search` interface in newer versions
- The framework uses streaming responses by default for better UX
- Tool calling in SimpleAgent uses text-based parsing, not native function calling
- Memory types have their own storage backends (no separate storage layer needed)
- Protocol support (MCP/A2A/ANP) is optional and requires additional dependencies
