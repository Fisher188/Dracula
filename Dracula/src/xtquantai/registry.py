from typing import Dict, Any

class ToolRegistry:
    """工具函数注册器"""
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, description: str, input_schema: Dict = None):
        """将函数注册为工具
        
        Args:
            name: 工具名称
            description: 工具描述
            input_schema: 输入参数模式
        """
        def decorator(func):
            self.tools[name] = {
                "function": func,
                "description": description,
                "input_schema": input_schema or {}
            }
            return func
        return decorator

# 创建全局注册器实例
tool_registry = ToolRegistry()

# 导出实例
__all__ = ['tool_registry'] 