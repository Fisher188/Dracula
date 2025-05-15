"""
工具函数模块
包含所有注册到 MCP 服务器的工具函数
"""
import os
import importlib
import pkgutil

# 自动导入同目录下所有模块
__all__ = []

# 获取当前包的路径
package_dir = os.path.dirname(__file__)

# 遍历当前目录下的所有模块
for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
    # 排除自身
    if module_name != "__init__":
        # 动态导入模块
        module = importlib.import_module(f".{module_name}", __package__)
        # 将模块名添加到 __all__ 列表
        __all__.append(module_name)
        # 将模块添加到全局命名空间
        globals()[module_name] = module
