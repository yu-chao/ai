# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

PlantMate Agents 是一个基于 OpenAI 原生 API 构建的灵活、可扩展的多智能体框架。它提供了智能体开发模式、工具系统、记忆管理、RAG 能力、协议支持（MCP、A2A、ANP）、评估框架和强化学习训练。

## 开发命令

### 安装

```bash
# 核心安装
pip install -e .

# 带可选依赖的安装（extras）
pip install -e ".[search]"      # 搜索功能 (Tavily, SerpApi)
pip install -e ".[memory]"      # 记忆系统 (Qdrant, Neo4j, spaCy)
pip install -e ".[rag]"         # RAG 系统 (scikit-learn, transformers, torch)
pip install -e ".[protocols]"   # 协议支持 (fastmcp, a2a-sdk)
pip install -e ".[evaluation]"  # 评估系统
pip install -e ".[rl]"          # 强化学习训练系统
pip install -e ".[all]"         # 安装所有功能
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_specific.py

# 详细输出模式
pytest -v --tb=short
```

### 代码质量

```bash
# 使用 Black 格式化代码
black plantmate_agents/

# 使用 isort 排序导入
isort plantmate_agents/

# 使用 mypy 进行类型检查
mypy plantmate_agents/
```

### 运行 FastAPI 服务器

```bash
# 开发服务器（带自动重载）
python -m server.app

# 或直接使用 uvicorn
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

### 测试 API

```bash
# 运行 API 测试
python test_api.py
```

## 架构

### 核心组件 (`plantmate_agents/core/`)

- **`PlantmateAgentsLLM`** (llm.py): 统一的 LLM 客户端，支持多个提供商（OpenAI、DeepSeek、通义千问、ModelScope、Kimi、智谱、Ollama、vLLM）。从环境变量或参数自动检测提供商。默认通过 `think()` 方法使用流式响应。
- **`Config`** (config.py): 使用 Pydantic 模型的配置管理
- **`Message`** (message.py): 对话历史的消息数据结构
- **`Agent`** (agent.py): 所有智能体实现的抽象基类

### 智能体模式 (`plantmate_agents/agents/`)

所有智能体都继承自基础的 `Agent` 类：

- **`SimpleAgent`**: 基础对话智能体，支持可选的工具调用。使用 `[TOOL_CALL:tool_name:params]` 格式从文本中解析工具调用。支持多步骤工具迭代。
- **`FunctionCallAgent`**: 使用 OpenAI 原生函数调用
- **`ReActAgent`**: 推理+行动模式，带有思考/行动/观察循环
- **`ReflectionAgent`**: 最终响应前的自我反思
- **`PlanAndSolveAgent`**: 先规划，后执行
- **`ToolAwareSimpleAgent`**: SimpleAgent 的工具感知变体

### 工具系统 (`plantmate_agents/tools/`)

- **`Tool` (base.py)**: 带有 `expandable` 标志的抽象基类。工具可以使用 `@tool_action` 装饰器展开为多个子工具。支持 OpenAI 函数调用模式转换。
- **`ToolRegistry` (registry.py)**: 管理工具注册和执行。默认自动展开可展开的工具。
- **内置工具** (builtin/): SearchTool、CalculatorTool、MemoryTool、RAGTool、NoteTool、TerminalTool、协议工具（MCP/A2A/ANP）、评估工具

### 记忆系统 (`plantmate_agents/memory/`)

- **`MemoryManager` (manager.py)**: 所有记忆类型的统一接口。处理记忆生命周期、重要性评分、遗忘、类型间整合。
- **记忆类型** (types/):
  - `WorkingMemory`: 短期记忆，容量有限
  - `EpisodicMemory`: 基于事件的经验，使用 Qdrant 向量存储
  - `SemanticMemory`: 事实性知识，使用 Neo4j 图存储
  - `PerceptualMemory`: 多模态感知数据
- **存储后端** (storage/): Qdrant（向量）、Neo4j（图）
- **RAG 流水线** (rag/): 文档处理、分块、嵌入、检索

### 协议支持 (`plantmate_agents/protocols/`)

- **MCP** (mcp/): 模型上下文协议 - 需要 `fastmcp`
- **A2A** (a2a/): 智能体间通信协议
- **ANP** (anp/): 智能体网络协议，用于服务发现

### 评估 (`plantmate_agents/evaluation/`)

基准评估框架，包括 BFCL、GAIA、LLM Judge 和胜率指标。

### 强化学习训练 (`plantmate_agents/rl/`)

使用 TRL 库的强化学习训练系统，用于智能体微调。

## 环境配置

复制 `.env.example` 为 `.env` 并配置：

### LLM 配置（统一格式）

框架从以下变量自动检测提供商：

```
LLM_MODEL_ID=your-model-name
LLM_API_KEY=your-api-key
LLM_BASE_URL=your-api-base-url
LLM_TIMEOUT=60
```

或使用特定提供商的变量（如 `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`DASHSCOPE_API_KEY`）。

### 数据库配置

- **Qdrant**（向量存储）: `QDRANT_URL`、`QDRANT_API_KEY`、`QDRANT_COLLECTION`
- **Neo4j**（图存储）: `NEO4J_URI`、`NEO4J_USERNAME`、`NEO4J_PASSWORD`

### 搜索工具

- **Tavily**: `TAVILY_API_KEY`
- **SerpApi**: `SERPAPI_API_KEY`

### 其他

- **嵌入**: `EMBED_MODEL_TYPE`、`EMBED_MODEL_NAME`、`EMBED_API_KEY`
- **GitHub**: `GITHUB_PERSONAL_ACCESS_TOKEN`
- **HuggingFace**: `HF_TOKEN`

## 关键设计模式

### 创建工具

```python
from plantmate_agents.tools import Tool, ToolParameter, tool_action

class MyTool(Tool, expandable=True):
    def __init__(self):
        super().__init__(name="my_tool", description="...", expandable=True)

    @tool_action("my_action", "执行某个操作")
    def _my_action(self, param: str, count: int = 1) -> str:
        '''操作描述

        Args:
            param: 参数描述
            count: 数量描述
        '''
        return "result"
```

### 使用智能体

```python
from plantmate_agents import PlantmateAgentsLLM, SimpleAgent

llm = PlantmateAgentsLLM()  # 从环境变量自动检测
agent = SimpleAgent(name="assistant", llm=llm, system_prompt="...")
response = agent.run("用户输入")
```

### 记忆集成

```python
from plantmate_agents.memory import MemoryManager

memory = MemoryManager(user_id="user123")
memory.add_memory("内容", memory_type="episodic", importance=0.8)
results = memory.retrieve_memories("查询", limit=5)
```

## 重要说明

- **需要 Python 3.10 或更高版本**
- **BFCL 评估** 需要 `numpy==1.26.4`，与核心依赖 `numpy>=2.0` 冲突 - 必须使用独立的虚拟环境
- **Qdrant 客户端**: 版本固定为 `<1.16.0`，因为新版本移除了 `search` 接口
- 框架默认使用流式响应以提供更好的用户体验
- SimpleAgent 中的工具调用使用基于文本的解析，而非原生函数调用
- 记忆类型有自己的存储后端（不需要单独的存储层）
- 协议支持（MCP/A2A/ANP）是可选的，需要额外的依赖
