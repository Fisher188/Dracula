import asyncio
import os
import tempfile
from .single_stock_backtest import run_backtest

async def test_backtest_workflow():
    """测试回测工作流程"""
    print("======= 开始测试回测功能 =======")
    
    # 回测参数
    stock_code = "600050.SH"
    signal = "Bk:= MA(CLOSE,5)>MA(CLOSE,10); bp:= MA(CLOSE,5)<MA(CLOSE,10);"
    
    # 测试临时目录保存
    temp_dir = tempfile.gettempdir()
    print(f"测试保存到临时目录: {temp_dir}")
    
    # 测试交互式图表
    print("\n1. 测试生成交互式图表...")
    result = await run_backtest(
        stock_code=stock_code,
        signal=signal,
        output_type="interactive",
        save_path=temp_dir,
        auto_open=True
    )
    
    print(f"返回状态: {result.get('status')}")
    print(f"返回消息: {result.get('message')}")
    print(f"文件路径: {result.get('file_path')}")
    if os.path.exists(result.get('file_path', '')):
        print(f"文件确实存在，大小: {os.path.getsize(result.get('file_path'))} 字节")
    else:
        print(f"警告: 文件不存在!")
    
    # 测试静态图表
    print("\n2. 测试生成静态图表...")
    result = await run_backtest(
        stock_code=stock_code,
        signal=signal,
        output_type="static",
        save_path=temp_dir,
        auto_open=True
    )
    
    print(f"返回状态: {result.get('status')}")
    print(f"返回消息: {result.get('message')}")
    print(f"文件路径: {result.get('file_path')}")
    if os.path.exists(result.get('file_path', '')):
        print(f"文件确实存在，大小: {os.path.getsize(result.get('file_path'))} 字节")
    else:
        print(f"警告: 文件不存在!")
    
    # 测试仅数据返回
    print("\n3. 测试仅返回数据...")
    result = await run_backtest(
        stock_code=stock_code,
        signal=signal,
        output_type="data",
        auto_open=False
    )
    
    print(f"返回状态: {result.get('status')}")
    print(f"返回消息: {result.get('message')}")
    if "result" in result and "summary" in result["result"]:
        print(f"回测结果摘要: {result['result']['summary']}")
    
    print("\n======= 测试完成 =======")

if __name__ == "__main__":
    asyncio.run(test_backtest_workflow()) 