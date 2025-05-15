# xtquantai

xtquantai 是一个基于 Model Context Protocol (MCP) 的服务器，它将迅投 (xtquant) 量化交易平台的功能与人工智能助手集成，使 AI 能够直接访问和操作量化交易数据和功能。

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 功能特点

XTQuantAI 提供以下核心功能(陆续更新中，欢迎大家提交新创意)：

### 基础数据查询
- **获取交易日期** (`get_trading_dates`) - 获取指定市场的交易日期
- **获取板块股票列表** (`get_stock_list`) - 获取特定板块的股票列表
- **获取股票详情** (`get_instrument_detail`) - 获取股票的详细信息

### 行情数据
- **获取历史行情数据** (`get_history_market_data`) - 获取股票的历史行情数据
- **获取最新行情数据** (`get_latest_market_data`) - 获取股票的最新行情数据
- **获取完整行情数据** (`get_full_market_data`) - 获取股票的完整行情数据

### 图表和可视化
- **创建图表面板** (`create_chart_panel`) - 创建股票图表面板，支持各种技术指标
- **创建自定义布局** (`create_custom_layout`) - 创建自定义的图表布局，可以指定指标名称、参数名和参数值

## 安装

⚠️ 注意
1. QMT 生态系统目前仅支持 Windows，因此以下均在 Windows 环境实现
2. Windows 环境目前在实现 MCP 过程中有不少细节，需要注意

### 前提条件
- Python 3.11 或更高版本
- 迅投 QMT 或投研终端

### 下载即可
```bash
git clone https://gitee.com/xtquant/xtquantai.git
```

或者直接下载压缩包。你可以下载到任意文件夹，只要最后能够找到 xtquantai 的具体地址即可，最好去文件夹里直接去复制地址。

## 使用方法

### 与 Cursor 的集成

#### Windows（QMT/投研端目前仅支持 Windows，需在 Windows 环境）

在 Cursor 中配置 MCP 服务器：

在当前项目建立 `.cursor` 文件夹，在该文件夹下建立 `mcp.json` 文件，则 Cursor 编辑器会自动添加该 mcp 工具

```json
{
  "mcpServers": {
    "xtquantai": {
      "command": "python",
      "args": ["-m", "xtquantai.server"]
    }
  }
}
```

### 核心组件说明

- **根目录配置文件**:
  - `pyproject.toml`: 定义项目的元数据、依赖和构建配置

- **源代码目录 (src/)**:
  - `xtquantai/`: 主要功能实现目录
    - `server.py`: MCP 服务器的核心实现，包含所有交易相关的工具函数
    - `__init__.py`: 包的初始化文件，导出主要接口

- **编辑器配置 (.cursor/)**:
  - `mcp.json`: Cursor 编辑器的 MCP 服务器配置文件

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 致谢

- [迅投科技](https://www.thinktrader.net/) 提供的量化交易平台
- [Model Context Protocol](https://modelcontextprotocol.io/) 提供的 AI 集成框架
