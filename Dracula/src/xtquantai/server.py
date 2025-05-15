import asyncio
from typing import Optional, List, Dict, Any, Callable, Union
import json
import sys
import inspect
from datetime import datetime
import random  # 新增：用于生成随机价格
import mcp.server.stdio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from .registry import tool_registry

# 导入所有工具函数
from . import tools

# 使用装饰器注册工具
@tool_registry.register(
    name="test_connection",
    description="测试服务器连接",
    input_schema={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "测试消息",
                "default": "hello"
            }
        }
    }
)
async def test_connection(message: str = "hello") -> Dict:
    """测试连接工具函数"""
    return {
        "type": "test_result",
        "message": f"服务器收到消息: {message}",
        "timestamp": datetime.now().isoformat()
    }


# 可以继续添加更多工具
# @tool_registry.register(...)
# async def another_tool(...):
#     ...

async def handle_list_resources(server) -> list[types.Resource]:
    """
    List available resources.
    """
    return []

async def handle_read_resource(server, uri) -> str:
    """
    Read a specific resource.
    """
    raise ValueError(f"Unsupported URI: {uri}")

async def handle_list_prompts(server) -> list[types.Prompt]:
    """
    List available prompts.
    """
    return []

async def handle_get_prompt(
    server, name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Get a specific prompt.
    """
    raise ValueError(f"Unknown prompt: {name}")

async def handle_list_tools(server) -> list[types.Tool]:
    """
    List available tools.
    """
    print("handle_list_tools被调用，返回所有工具")
    tools = []
    
    # 自动从注册表收集所有工具
    for name, tool_info in tool_registry.tools.items():
        tools.append(types.Tool(
            name=name,
            description=tool_info["description"],
            inputSchema=tool_info["input_schema"]
        ))
    
    print(f"返回的工具数 {len(tools)}")
    return tools

async def handle_call_tool(
    server, name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Call a specific tool.
    """
    # 检查工具是否存在
    if name in tool_registry.tools:
        tool_func = tool_registry.tools[name]["function"]
        kwargs = arguments or {}
        
        # 调用工具函数
        result = await tool_func(**kwargs)
        
        # 将结果转换为文本内容
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    else:
        raise ValueError(f"未知工具: {name}")

async def async_start_server():
    server = Server("xtquantaibst")
    
    # 注册所有处理函数
    server.list_resources()(lambda: handle_list_resources(server))
    server.read_resource()(lambda uri: handle_read_resource(server, uri))
    server.list_prompts()(lambda: handle_list_prompts(server))
    server.get_prompt()(lambda name, arguments: handle_get_prompt(server, name, arguments))
    server.list_tools()(lambda: handle_list_tools(server))
    server.call_tool()(lambda name, arguments: handle_call_tool(server, name, arguments))
    
    print("\n在server.py中打印所有工具:")
    tools = await handle_list_tools(server)
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name} - {tool.description}")
    
    print("Starting MCPServer...", file=sys.stderr)
    
    # 使用 stdio 运行服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="xtquantaibst",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def run_server():
    asyncio.run(async_start_server())

if __name__ == "__main__":
    run_server()
