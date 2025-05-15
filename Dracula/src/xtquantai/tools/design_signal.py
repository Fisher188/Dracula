from typing import Dict, Any
from ..registry import tool_registry

def format_vba_code(code: str) -> str:
    """格式化VBA代码，确保语句以分号结尾"""
    # 移除空行
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    # 处理每一行
    formatted_lines = []
    for line in lines:
        # 如果行以注释开头，直接添加
        if line.startswith('//'):
            formatted_lines.append(line)
            continue
            
        # 如果行已经以分号结尾，直接添加
        if line.endswith(';'):
            formatted_lines.append(line)
            continue
            
        # 如果行以赋值符号结尾，添加分号
        if line.endswith(':'):
            formatted_lines.append(line)
            continue
            
        # 处理条件组合
        if line.startswith('bk:=') or line.startswith('bp:='):
            # 如果是条件组合的开始行
            if line.endswith('&&') or line.startswith('||'):
                formatted_lines.append(line)
                continue
            # 如果是条件组合的中间行
            if line.startswith('&&') or line.startswith('||'):
                formatted_lines.append(line)
                continue
            # 如果是条件组合的最后一行
            if not line.endswith(';'):
                line += ';'
            formatted_lines.append(line)
            continue
            
        # 处理指标计算
        if ':=' in line:
            # 如果行包含赋值操作符
            if not line.endswith(';'):
                line += ';'
            formatted_lines.append(line)
            continue
            
        # 其他情况添加分号
        formatted_lines.append(line + ';')
    
    return '\n'.join(formatted_lines)

def format_condition(condition: str) -> str:
    """格式化条件组合"""
    # 移除多余的空格
    condition = ' '.join(condition.split())
    
    # 如果条件中包含注释，需要特殊处理
    if '//' in condition:
        parts = condition.split('//')
        main_cond = parts[0].strip()
        comment = '//' + parts[1].strip()
        
        # 确保主条件以分号结尾
        if not main_cond.endswith(';'):
            main_cond += ';'
            
        return f"{main_cond} {comment}"
    
    # 处理多行条件组合
    if '\n' in condition:
        lines = condition.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('&&') or line.startswith('||'):
                formatted_lines.append(line)
            else:
                if not line.endswith(';'):
                    line += ';'
                formatted_lines.append(line)
        return '\n'.join(formatted_lines)
    
    # 普通条件处理
    if not condition.endswith(';'):
        condition += ';'
    
    return condition

def extract_condition(condition: str) -> str:
    """从条件字符串中提取实际的条件表达式"""
    # 移除注释
    if '//' in condition:
        condition = condition.split('//')[0].strip()
    
    # 移除 bk:= 或 bp:= 前缀
    if condition.startswith('bk:='):
        condition = condition[4:].strip()
    elif condition.startswith('bp:='):
        condition = condition[4:].strip()
    
    # 如果条件为空，返回空字符串
    if not condition:
        return ""
    
    return condition

def format_indicators(indicators: str) -> str:
    """格式化指标计算代码"""
    lines = indicators.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 处理注释
        if line.startswith('//'):
            formatted_lines.append(line)
            continue
            
        # 处理指标计算
        if ':=' in line:
            # 移除可能存在的 VAR 关键字
            if line.startswith('VAR '):
                line = line[4:].strip()
            if not line.endswith(';'):
                line += ';'
            formatted_lines.append(line)
            continue
            
        # 其他情况
        if not line.endswith(';'):
            line += ';'
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

SIGNAL_TEMPLATE = f"""
//……………………写入你的指标判断……………………
{{inputs}}

{{indicators}}
//………………………………………………………………

bk:= {{buy_condition}};//////////开仓条件

bp:= {{sell_condition}};////平仓条件
"""

@tool_registry.register(
    name="create_ma_cross_signal",
    description="创建均线交叉策略信号",
    input_schema={
        "type": "object",
        "properties": {
            "fast_period": {
                "type": "integer",
                "description": "快线周期",
                "default": 5
            },
            "slow_period": {
                "type": "integer",
                "description": "慢线周期",
                "default": 34
            }
        }
    }
)
async def create_ma_cross_signal(
    fast_period: int = 5,
    slow_period: int = 34
) -> str:
    """
    创建均线交叉策略信号
    
    Args:
        fast_period: 快线周期，默认5
        slow_period: 慢线周期，默认34
    
    Returns:
        策略信号代码字符串
    """
    inputs = f"""
input:N1({fast_period},1,100,1);
input:N2({slow_period},1,120,1);
"""

    indicators = f"""
ma1:=ma(c,N1);
ma2:=ma(c,N2);
"""

    buy_condition = "cross(ma1,ma2)"
    sell_condition = "cross(ma2,ma1)"

    return SIGNAL_TEMPLATE.format(
        inputs=inputs,
        indicators=indicators,
        buy_condition=buy_condition,
        sell_condition=sell_condition
    )

@tool_registry.register(
    name="create_custom_signal",
    description="创建自定义策略信号",
    input_schema={
        "type": "object",
        "required": ["inputs", "indicators", "buy_condition", "sell_condition"],
        "properties": {
            "inputs": {
                "type": "string",
                "description": "输入参数定义，如'input:N1(5,1,100,1);'"
            },
            "indicators": {
                "type": "string",
                "description": "指标计算逻辑，注意：不要使用VAR关键字，直接使用:=赋值即可"
            },
            "buy_condition": {
                "type": "string",
                "description": "买入条件"
            },
            "sell_condition": {
                "type": "string",
                "description": "卖出条件"
            }
        }
    }
)
async def create_custom_signal(
    inputs: str,
    indicators: str,
    buy_condition: str,
    sell_condition: str
) -> str:
    """
    创建自定义策略信号
    
    Args:
        inputs: 输入参数定义，如'input:N1(5,1,100,1);'
        indicators: 指标计算逻辑，注意：不要使用VAR关键字，直接使用:=赋值即可
        buy_condition: 买入条件
        sell_condition: 卖出条件
    
    Returns:
        策略信号代码字符串
        
    Example:
        >>> indicators = '''
        >>> // 计算RSI指标
        >>> RSI:=RSI(CLOSE,RSI_PERIOD);
        >>> 
        >>> // 计算MACD指标
        >>> DIF:=EMA(CLOSE,MACD_FAST)-EMA(CLOSE,MACD_SLOW);
        >>> DEA:=EMA(DIF,MACD_SIGNAL);
        >>> MACD:=DIF-DEA;
        >>> '''
    """
    # 格式化输入的代码
    formatted_inputs = format_vba_code(inputs)
    formatted_indicators = format_indicators(indicators)
    
    # 直接使用传入的买卖条件，不需要提取
    bk_condition = f"bk:= {buy_condition};" if buy_condition else "bk:= ;"
    bp_condition = f"bp:= {sell_condition};" if sell_condition else "bp:= ;"
    
    return f"""
//……………………写入你的指标判断……………………
{formatted_inputs}

{formatted_indicators}
//………………………………………………………………

{bk_condition}//////////开仓条件

{bp_condition}////平仓条件
"""