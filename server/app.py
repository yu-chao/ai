"""
FastAPI HTTP 请求演示应用
展示各种 HTTP 方法和请求处理方式
"""
from fastapi.responses import Response, StreamingResponse
from fastapi import FastAPI, HTTPException, Query, Depends
import uvicorn
import json
import asyncio

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
from plantmate_agents import (
    HelloAgentsLLM,
    SimpleAgent
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="PlantMate Agent API",
    description="智能体系统的 HTTP API 演示",
    version="1.0.0"
)

# 全局LLM和Agent实例（避免每次请求重新创建）
_llm_instance = None
_agent_instance = None

def get_llm():
    """获取或创建LLM实例（单例模式）"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = HelloAgentsLLM()
    return _llm_instance

def get_agent():
    """获取或创建Agent实例（单例模式）"""
    global _agent_instance
    if _agent_instance is None:
        llm = get_llm()
        _agent_instance = SimpleAgent(
            name="助手",
            llm=llm,
            system_prompt="你是一个有用的AI助手，请用中文回答问题。"
        )
    return _agent_instance

# === GET 请求演示 ===

@app.get("/")
async def root():
    """根路径 - 欢迎信息"""
    return {
        "message": "欢迎使用 PlantMate Agent API",
        "version": "1.0.0",
        "docs": "/docs",  # FastAPI 自动生成的 API 文档
        "redoc": "/redoc"  # 另一个文档界面
    }

@app.post("/chat")
async def chat_with_agent(
    message: str = Query(..., description="用户消息")
):
    print(f"message--------: {message}")
    try:
        return demo_simple_agent(message);
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def demo_simple_agent(message:str):
    """演示SimpleAgent - 基础对话"""
    print("\n" + "="*60)
    print("🤖 SimpleAgent 演示 - 基础对话Agent")
    print("="*60)

    # 创建LLM实例
    llm = HelloAgentsLLM()

    # 创建简单Agent
    agent = SimpleAgent(
        name="助手",
        llm=llm,
        system_prompt="你是一个有用的AI助手，请用中文回答问题。"
    )

    # 测试对话
    return agent.run(message)



async def generate_stream_response(message: str, agent):
    """生成流式响应"""
    try:
        # 发送开始标记
        start_data = {
            "type": "start",
            "message": "开始处理您的请求...",
            "timestamp": str(asyncio.get_event_loop().time())
        }
        yield f"data: {json.dumps(start_data, ensure_ascii=False)}\n\n"

        # 获取流式响应（处理同步生成器）
        stream_generator = agent.stream_run(message)
        for chunk in stream_generator:
            if chunk:  # 确保chunk不为空
                chunk_data = {
                    "type": "chunk",
                    "content": chunk,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                # 让出控制权，避免阻塞
                await asyncio.sleep(0.001)

        # 发送结束标记
        end_data = {
            "type": "end",
            "message": "响应完成",
            "timestamp": str(asyncio.get_event_loop().time())
        }
        yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"

    except Exception as e:
        # 发送错误标记
        error_data = {
            "type": "error",
            "message": f"处理请求时发生错误: {str(e)}",
            "timestamp": str(asyncio.get_event_loop().time())
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.post("/api/chat/stream")
async def chat_stream(
    message: str = Query(..., min_length=1, max_length=2000, description="用户消息"),
    agent = Depends(get_agent)
):
    """
    流式聊天接口

    返回Server-Sent Events (SSE)格式的流式响应
    """
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    return StreamingResponse(
        generate_stream_response(message.strip(), agent),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )
    


# 启动服务器（仅在直接运行此文件时执行）
if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # 直接传递 FastAPI 应用实例
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )