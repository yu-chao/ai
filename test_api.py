#!/usr/bin/env python3
"""测试 FastAPI 接口的脚本"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_get_root():
    """测试根路径"""
    print("=== 测试根路径 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_agents():
    """测试获取智能体列表"""
    print("=== 测试获取智能体列表 ===")
    response = requests.get(f"{BASE_URL}/agents")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_create_agent():
    """测试创建新智能体"""
    print("=== 测试创建新智能体 ===")
    data = {
        "name": "测试智能体",
        "description": "用于测试的智能体",
        "model": "gpt-4",
        "temperature": 0.5
    }
    response = requests.post(f"{BASE_URL}/agents", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    return response.json() if response.status_code == 200 else None

def test_get_single_agent(agent_id):
    """测试获取单个智能体"""
    print(f"=== 测试获取智能体 {agent_id} ===")
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    print()

def test_chat():
    """测试聊天功能"""
    print("=== 测试聊天功能 ===")
    params = {
        "message": "你好，请介绍一下你自己"
    }
    response = requests.post(f"{BASE_URL}/chat", params=params)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_stream_chat():
    """测试流式聊天功能"""
    print("=== 测试流式聊天功能 ===")
    params = {
        "message": "请用几句话介绍一下人工智能的发展历程"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/chat/stream", params=params, stream=True)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("接收流式响应:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # 移除 'data: ' 前缀
                            print(f"[{data['type']}] {data.get('content', data.get('message', ''))}")
                        except json.JSONDecodeError:
                            print(f"原始数据: {line_str}")
        else:
            print(f"错误: {response.text}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    try:
        # test_get_root()
        # test_chat()
        test_stream_chat()
        print("流式测试完成！")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 FastAPI 服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")