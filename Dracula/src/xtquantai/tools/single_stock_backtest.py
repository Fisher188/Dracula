from typing import Dict, Any
from ..registry import tool_registry
import xtquant.xtdata as xtdata
import pandas as pd
import numpy as np

# 设置pandas显示所有列
pd.set_option('display.max_columns', None)

def process_backtest_result(df: pd.DataFrame) -> Dict[str, Any]:
    """处理回测结果DataFrame，转换为可序列化的字典格式"""
    
    # 获取最后一行数据（最终结果）
    final_result = df.iloc[-1].to_dict()
    
    # 处理所有的NaN值和None值
    for k, v in final_result.items():
        if v is None or (isinstance(v, (float, np.float64)) and np.isnan(v)):
            final_result[k] = 0.0  # 将None和NaN转换为0.0
        elif isinstance(v, np.number):
            final_result[k] = float(v)
        else:
            final_result[k] = v
    
    # 提取关键指标，添加默认值处理
    summary = {
        "总收益率": float(final_result.get("策略收益", 0.0)),
        "最大回撤": float(final_result.get("最大回撤", 0.0)),
        "胜率": float(final_result.get("胜率", 0.0)),
        "交易次数": int(final_result.get("交易次数", 0)),
        "收益回撤比": float(final_result.get("收益回撤比", 0.0))
    }
    
    # 生成每日数据，添加默认值处理
    daily_data = []
    for idx, row in df.iterrows():
        daily_record = {
            "date": idx,
            "timestamp": int(row.get("time", 0)),
            "strategy_value": float(row.get("策略收益", 0.0)) if not pd.isna(row.get("策略收益")) else 0.0,
            "holding_period": int(row.get("持仓周期", 0)) if not pd.isna(row.get("持仓周期")) else 0,
            "holding_return": float(row.get("持仓收益", 0.0)) if not pd.isna(row.get("持仓收益")) else 0.0,
            "drawdown": float(row.get("最近回撤", 0.0)) if not pd.isna(row.get("最近回撤")) else 0.0
        }
        daily_data.append(daily_record)
    
    return {
        "summary": summary,
        "final_result": final_result,
        "daily_data": daily_data
    }

@tool_registry.register(
    name="run_single_stock_backtest",
    description="运行单个股票的策略回测",
    input_schema={
        "type": "object",
        "required": ["stock_code", "signal"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600050.SH'"
            },
            "signal": {
                "type": "string",
                "description": "策略信号代码，包含买卖条件的VBA代码"
            },
            "period": {
                "type": "string",
                "description": "K线周期",
                "default": "1d"  # 默认周期为1天，也可以是 1m、5m
            },
            "start_time": {
                "type": "string",
                "description": "开始时间，格式如'20240101000000'",
                "default": "20240101000000"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间，格式如'20241231150000'",
                "default": "20241231150000"
            },
            "count": {
                "type": "integer",
                "description": "数据条数，-1表示全部",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权类型",
                "default": "front_ratio"
            }
        }
    }
)
async def run_single_stock_backtest(
    stock_code: str,
    signal: str,
    period: str = "1d",  # 默认周期为1天，也可以是 1m、5m
    start_time: str = "20240101000000",
    end_time: str = "20241231150000",
    count: int = -1,
    dividend_type: str = "front_ratio"
) -> Dict[str, Any]:
    """
    运行单个股票的策略回测
    
    Args:
        stock_code: 股票代码，如'600050.SH'
        signal: 策略信号代码，包含买卖条件的VBA代码
        period: K线周期，默认'1d'
        start_time: 开始时间，默认'20240101000000'
        end_time: 结束时间，默认'20241231150000'
        count: 数据条数，默认-1表示全部
        dividend_type: 除权类型，默认'front_ratio'
    
    Returns:
        回测结果字典，包含:
        - summary: 回测汇总指标
        - final_result: 最后一天的完整结果
        - daily_data: 每日回测数据
    """
    vba_template = f"""
VARIABLE:cj1=0,hszhishu:=0,BBD=0,zhishu=0,tmp=0,tmpshort=0,buypoint=0,sellpoint=0,profit=0,TestHolding=0,maxzhishu=0,huiche=0,maxhuiche=0,DCS=0,maxprofit=0,maxDhuiche=0,Dhuiche=0,maxshortprofit=0, hs300bp=0,hstmp=0,TMPzhishu=0,hs300bp=0;

回测板块 : '沪深300';
买入金额 : 50000, nodraw; 

hs300c:=callstock('sh000300',vtclose,-1,0);

buy := 0;
sell1 := 0;

M:=BARSLAST(date<>REF(date,1))+1;
t:=BARSLAST(TestHolding=0),nodraw;
持仓周期：t,nodraw()；

zst:=(hs300c-ref(hs300c,t))/ref(hs300c,t);
ggt:=(c-ref(c,t))/ref(c,t);
CJt:= 1*(GGt) ,NOAXIS;
持仓收益：CJt*100，nodraw();
dcCJt:= 1*(GGt-zst) ,NOAXIS;

cjt1:=if(TestHolding>0,(cjt-ref(cjt,1))*100，0）,LINETHICK0;
dccjt1:=if(TestHolding>0,(dccjt-ref(dccjt,1))*100，0）,LINETHICK0；

qzzhishu:=1*sum(cjt1,0),NOAXIS;
策略收益：qzzhishu，noaxis();
qzdczhishu:=1*sum(dccjt1,0),NOAXIS;

{signal}
;

nn:=0;

IF (ref(Bk,nn) and not(bp) and  TestHolding=0  ） THEN BEGIN
    TestHolding:=1;    
    BBD:=BARPOS;
    DRAWTEXT(1 ,H+4,'买入');
    hs300bp:=callstock('sh000300',vtclose,-1,0); 
    buypoint:=close;    
    tmp:=zhishu;
    hstmp:=hszhishu;
    buy:=1;
END    

IF (ref(bp,nn) AND TestHolding>0   ) THEN BEGIN
    TestHolding:=0;
    BBD:=0;
    DRAWTEXT(1,H+1,'卖出');
    hs300sp:=callstock('sh000300',vtclose,-1,0);    
    thisprofit:=(close-buypoint)/buypoint;
    HSthisprofit:=(hs300sp-hs300bp)/hs300bp;
    HSzhishu:=(hstmp+hsthisprofit);
    zhishu:=(tmp+thisprofit-0.003);
    buypoint:=0;
    hs300bp:=0;
    profit:=profit+thisprofit;
    DCS:=DCS+1;
    sell1:=1;
END

指数:=zhishu,NOAXIS,coloryellow;
对应指数:=hszhishu,NOAXIS,colorwhite;
对冲:=指数-对应指数,NOAXIS,colorblue;

交易次数:DCS,LINETHICK0;

最近回撤:hhv(策略收益,0)-策略收益,nodraw();
最大回撤:hhv(（hhv(策略收益,0)-策略收益）,0),nodraw();

ttttt:=TestHolding,LINETHICK0;
平均收益:策略收益/交易次数,LINETHICK0;
收益回撤比:策略收益/最大回撤,nodraw();

胜率:count(指数>ref(指数,1),0)/DCS,LINETHICK0;
"""

    try:
        # 获取回测结果
        result = xtdata.get_vba_func_result(
            [vba_template],
            stock_code,
            period,
            start_time,
            end_time,
            count,
            dividend_type
        )
        
        # 如果结果是DataFrame，处理它
        if isinstance(result, pd.DataFrame):
            processed_result = process_backtest_result(result)
        else:
            # 如果不是DataFrame，可能是其他格式的结果
            processed_result = {
                "raw_result": str(result),
                "error": "Unexpected result format"
            }
            
        # 添加回测参数信息
        processed_result["parameters"] = {
            "stock_code": stock_code,
            "period": period,
            "start_time": start_time,
            "end_time": end_time,
            "count": count,
            "dividend_type": dividend_type
        }
        
        return processed_result
        
    except Exception as e:
        return {
            "error": str(e),
            "parameters": {
                "stock_code": stock_code,
                "period": period,
                "start_time": start_time,
                "end_time": end_time
            }
        }

def visualize_backtest_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将回测结果可视化，生成图表展示回测表现
    
    Args:
        result: 回测结果字典
    
    Returns:
        包含图表路径的字典
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import io
        import base64
        import tempfile
        import os
        from datetime import datetime
        
        # 配置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']  # 用来正常显示中文
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        # 如果结果中有错误，直接返回
        if "error" in result:
            return result
        
        # 提取数据
        daily_data = result.get("daily_data", [])
        if not daily_data:
            return {**result, "visual_data": {"error": "没有足够的数据生成图表"}}
        
        # 转换数据格式
        dates = []
        strategy_values = []
        drawdowns = []
        holdings = []
        
        for day in daily_data:
            date_str = day.get("date")
            try:
                # 尝试解析日期
                if isinstance(date_str, str):
                    if len(date_str) == 8:  # 格式如 "20240101"
                        date = datetime.strptime(date_str, "%Y%m%d")
                    else:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    date = date_str  # 如果已经是日期类型
                
                dates.append(date)
                strategy_values.append(day.get("strategy_value", 0))
                drawdowns.append(day.get("drawdown", 0))
                holdings.append(day.get("holding_period", 0) > 0)  # 是否持仓
            except Exception:
                continue
        
        if not dates:
            return {**result, "visual_data": {"error": "日期格式转换错误"}}
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
        fig.subplots_adjust(hspace=0.3)
        
        # 绘制策略收益曲线
        ax1.plot(dates, strategy_values, 'b-', linewidth=2, label='策略收益率(%)')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_title('策略回测结果 - ' + result.get("parameters", {}).get("stock_code", ""))
        ax1.set_ylabel('收益率(%)')
        ax1.legend(loc='upper left')
        
        # 标记持仓区间
        holding_changes = []
        for i in range(1, len(holdings)):
            if holdings[i] != holdings[i-1]:
                holding_changes.append((dates[i], holdings[i]))
        
        current_hold = False
        start_date = None
        for date, is_holding in holding_changes:
            if is_holding and not current_hold:  # 开始持仓
                start_date = date
                current_hold = True
            elif not is_holding and current_hold:  # 结束持仓
                ax1.axvspan(start_date, date, alpha=0.2, color='green')
                current_hold = False
        
        # 如果最后是持仓状态，画到最后
        if current_hold and start_date:
            ax1.axvspan(start_date, dates[-1], alpha=0.2, color='green')
        
        # 绘制回撤
        ax2.fill_between(dates, 0, drawdowns, color='red', alpha=0.5)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.set_ylabel('回撤(%)')
        ax2.set_xlabel('日期')
        
        # 格式化x轴日期
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # 添加关键指标文本
        summary = result.get("summary", {})
        textstr = '\n'.join((
            f'总收益率: {summary.get("总收益率", 0):.2f}%',
            f'最大回撤: {summary.get("最大回撤", 0):.2f}%',
            f'胜率: {summary.get("胜率", 0):.2f}',
            f'交易次数: {summary.get("交易次数", 0)}',
            f'收益回撤比: {summary.get("收益回撤比", 0):.2f}'
        ))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=9,
                verticalalignment='top', bbox=props)
        
        # 生成临时文件路径
        fd, temp_path = tempfile.mkstemp(suffix=".png", prefix=f"backtest_{result.get('parameters', {}).get('stock_code', 'unknown')}_")
        os.close(fd)
        
        # 保存图像到临时文件
        plt.savefig(temp_path, format='png', dpi=100)
        plt.close(fig)
        
        # 也生成一个base64字符串用于临时缓存，但不返回给API
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100) 
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        # 将图表路径添加到结果中，不包含大型base64数据
        visual_result = {
            **result,
            "visual_data": {
                "image_path": temp_path,
                "plot_type": "image/png"
            }
        }
        
        # 在临时字典中保存base64数据，但不返回给API
        visual_result["_temp_visual_data"] = {
            "plot_base64": image_base64
        }
        
        return visual_result
    
    except Exception as e:
        # 如果可视化过程中出现错误，记录错误但仍返回原始结果
        return {
            **result,
            "visual_data": {
                "error": str(e)
            }
        }

def display_backtest_result(result: Dict[str, Any]) -> None:
    """
    在IPython环境中直接显示回测结果图表
    
    Args:
        result: 回测结果字典，包含visual_data
    """
    try:
        from IPython.display import display, HTML, Image
        import base64
        
        # 检查结果中是否有可视化数据
        if "_temp_visual_data" in result and "plot_base64" in result["_temp_visual_data"]:
            # 使用临时存储的base64数据
            img_data = result["_temp_visual_data"]["plot_base64"]
            display(HTML(f'<img src="data:image/png;base64,{img_data}" />'))
        elif "visual_data" in result and "image_path" in result["visual_data"]:
            # 使用保存的图像文件
            image_path = result["visual_data"]["image_path"]
            display(Image(filename=image_path))
        else:
            print("没有可视化数据可显示")
            return
            
        # 显示回测结果摘要
        summary = result.get("summary", {})
        if summary:
            print("\n回测结果摘要:")
            print(f"总收益率: {summary.get('总收益率', 0):.2f}%")
            print(f"最大回撤: {summary.get('最大回撤', 0):.2f}%")
            print(f"胜率: {summary.get('胜率', 0):.2f}")
            print(f"交易次数: {summary.get('交易次数', 0)}")
            print(f"收益回撤比: {summary.get('收益回撤比', 0):.2f}")
    except ImportError:
        print("需要在IPython环境中运行才能显示图表")
    except Exception as e:
        print(f"显示图表时出错: {str(e)}")

def save_backtest_result_to_html(result: Dict[str, Any], file_path: str) -> str:
    """
    将回测结果保存为HTML文件，方便查看
    
    Args:
        result: 回测结果字典，包含visual_data
        file_path: 保存HTML的文件路径
        
    Returns:
        保存的文件路径
    """
    try:
        import base64
        import os
        
        # 检查是否有临时的base64数据
        if "_temp_visual_data" in result and "plot_base64" in result["_temp_visual_data"]:
            img_data = result["_temp_visual_data"]["plot_base64"]
        elif "visual_data" in result and "image_path" in result["visual_data"]:
            # 从图像文件读取并转换为base64
            with open(result["visual_data"]["image_path"], "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            raise ValueError("没有可视化数据可保存")
        
        summary = result.get("summary", {})
        parameters = result.get("parameters", {})
        
        # 构建HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>回测结果 - {parameters.get('stock_code', '')}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    border-radius: 5px;
                }}
                h1 {{
                    color: #333;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }}
                .summary {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .summary table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .summary td {{
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }}
                .summary td:first-child {{
                    font-weight: bold;
                    width: 30%;
                }}
                .chart-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>策略回测结果</h1>
                
                <div class="summary">
                    <h2>回测参数</h2>
                    <table>
                        <tr><td>股票代码</td><td>{parameters.get('stock_code', '')}</td></tr>
                        <tr><td>回测周期</td><td>{parameters.get('period', '')}</td></tr>
                        <tr><td>开始时间</td><td>{parameters.get('start_time', '')}</td></tr>
                        <tr><td>结束时间</td><td>{parameters.get('end_time', '')}</td></tr>
                    </table>
                </div>
                
                <div class="summary">
                    <h2>回测结果概览</h2>
                    <table>
                        <tr><td>总收益率</td><td>{summary.get('总收益率', 0):.2f}%</td></tr>
                        <tr><td>最大回撤</td><td>{summary.get('最大回撤', 0):.2f}%</td></tr>
                        <tr><td>胜率</td><td>{summary.get('胜率', 0):.2f}</td></tr>
                        <tr><td>交易次数</td><td>{summary.get('交易次数', 0)}</td></tr>
                        <tr><td>收益回撤比</td><td>{summary.get('收益回撤比', 0):.2f}</td></tr>
                    </table>
                </div>
                
                <div class="chart-container">
                    <h2>回测曲线</h2>
                    <img src="data:image/png;base64,{img_data}" alt="回测结果图表" />
                </div>
            </div>
        </body>
        </html>
        """
        
        # 保存HTML文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return file_path
    
    except Exception as e:
        raise ValueError(f"保存HTML文件时出错: {str(e)}")

def _detect_environment() -> str:
    """
    检测当前运行环境
    
    Returns:
        环境类型: 'ipython', 'jupyter', 'colab', 'terminal' 等
    """
    try:
        # 检查是否在IPython环境
        ip = get_ipython()
        
        if 'google.colab' in str(ip):
            return 'colab'
        elif 'zmqshell' in str(type(ip)):
            return 'jupyter'
        else:
            return 'ipython'
    except:
        # 非IPython环境
        return 'terminal'

def _get_desktop_path() -> str:
    """
    尝试获取用户桌面路径
    
    Returns:
        桌面路径，如果无法获取则返回空字符串
    """
    try:
        import os
        import platform
        
        system = platform.system()
        
        if system == 'Windows':
            # Windows系统
            try:
                # 首先尝试从注册表获取
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                if os.path.exists(desktop_path):
                    return desktop_path
            except:
                pass
                
            # 如果注册表方法失败，尝试标准路径
            paths_to_try = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                os.path.join(os.path.expanduser('~'), '桌面'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
                os.path.join(os.environ.get('USERPROFILE', ''), '桌面')
            ]
            
            for path in paths_to_try:
                if os.path.exists(path):
                    return path
                    
        elif system == 'Darwin':
            # macOS系统
            return os.path.join(os.path.expanduser('~'), 'Desktop')
        else:
            # Linux系统，尝试使用XDG标准
            try:
                import subprocess
                xdg_output = subprocess.check_output(['xdg-user-dir', 'DESKTOP'], universal_newlines=True).strip()
                if os.path.exists(xdg_output):
                    return xdg_output
            except:
                pass
            
            # 回退到家目录下的Desktop文件夹
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            if os.path.exists(desktop):
                return desktop
                
        # 尝试获取文档目录
        try:
            docs_path = None
            if system == 'Windows':
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
                docs_path = winreg.QueryValueEx(key, "Personal")[0]
            elif system == 'Darwin':
                docs_path = os.path.join(os.path.expanduser('~'), 'Documents')
            else:
                docs_path = os.path.join(os.path.expanduser('~'), 'Documents')
                
            if docs_path and os.path.exists(docs_path):
                return docs_path
        except:
            pass
                
        # 最后回退到当前目录
        return os.getcwd()
    except:
        # 所有方法都失败，返回当前目录
        return os.getcwd()

def _get_safe_file_path(base_dir: str, file_name: str, extension: str = "html") -> str:
    """
    获取安全的文件路径，确保目录存在
    
    Args:
        base_dir: 基础目录
        file_name: 文件名
        extension: 文件扩展名
        
    Returns:
        完整的文件路径
    """
    import os
    import tempfile
    
    # 如果base_dir为空或不存在，使用桌面路径
    if not base_dir or not os.path.exists(base_dir):
        # 尝试使用临时目录
        temp_dir = tempfile.gettempdir()
        print(f"使用临时目录保存文件: {temp_dir}")
        base_dir = temp_dir
    
    # 确保文件名安全
    safe_name = "".join([c for c in file_name if c.isalnum() or c in "._- "]).strip()
    if not safe_name:
        safe_name = "backtest_result"
        
    # 确保有扩展名
    if not extension.startswith("."):
        extension = "." + extension
        
    # 构建完整路径
    full_path = os.path.join(base_dir, f"{safe_name}{extension}")
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
        print(f"文件将保存到: {full_path}")
        return full_path
    except Exception as e:
        print(f"创建目录失败: {str(e)}，使用临时目录")
        # 如果创建目录失败，使用系统临时目录
        temp_path = os.path.join(tempfile.gettempdir(), f"{safe_name}{extension}")
        print(f"改为保存到: {temp_path}")
        return temp_path

def _open_file(file_path: str, silent: bool = False) -> bool:
    """
    尝试使用系统默认应用打开文件
    
    Args:
        file_path: 文件路径
        silent: 是否静默运行（不打印错误信息）
    
    Returns:
        是否成功打开
    """
    import os
    import platform
    import webbrowser
    import subprocess
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
        
    print(f"尝试打开文件: {file_path}")
    abs_path = os.path.abspath(file_path)
        
    try:
        # 尝试使用webbrowser模块（通常对HTML文件最可靠）
        print("尝试使用webbrowser打开...")
        if webbrowser.open('file://' + abs_path):
            print("使用webbrowser打开成功")
            return True
    except Exception as e:
        if not silent:
            print(f"webbrowser打开失败: {str(e)}")
    
    try:
        system = platform.system()
        print(f"检测到系统类型: {system}")
        
        if system == 'Darwin':  # macOS
            print("使用macOS open命令...")
            subprocess.run(['open', abs_path], check=True)
            return True
        elif system == 'Windows':  # Windows
            # 第一种方法：os.startfile
            try:
                print("尝试使用os.startfile...")
                os.startfile(abs_path)
                print("使用os.startfile打开成功")
                return True
            except Exception as e:
                if not silent:
                    print(f"os.startfile失败: {str(e)}")
                
            # 第二种方法：使用start命令
            try:
                print("尝试使用start命令...")
                result = subprocess.run(['start', abs_path], shell=True, check=False)
                print(f"start命令返回: {result.returncode}")
                if result.returncode == 0:
                    return True
            except Exception as e:
                if not silent:
                    print(f"start命令失败: {str(e)}")
                
            # 第三种方法：explorer
            try:
                print("尝试使用explorer...")
                result = subprocess.run(['explorer', abs_path], shell=True, check=False)
                print(f"explorer命令返回: {result.returncode}")
                if result.returncode == 0:
                    return True
            except Exception as e:
                if not silent:
                    print(f"explorer命令失败: {str(e)}")
        else:  # Linux
            try:
                print("尝试使用xdg-open...")
                subprocess.run(['xdg-open', abs_path], check=True)
                return True
            except Exception as e:
                if not silent:
                    print(f"xdg-open失败: {str(e)}")
    except Exception as e:
        if not silent:
            print(f"打开文件过程中出错: {str(e)}")
        
    print(f"所有打开方法均失败，请手动打开文件: {abs_path}")
    return False

@tool_registry.register(
    name="run_backtest",
    description="运行股票回测并直接显示结果",
    input_schema={
        "type": "object",
        "required": ["stock_code", "signal"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600050.SH'"
            },
            "signal": {
                "type": "string",
                "description": "策略信号代码，包含买卖条件的VBA代码"
            },
            "period": {
                "type": "string",
                "description": "K线周期",
                "default": "1d"
            },
            "start_time": {
                "type": "string",
                "description": "开始时间，格式如'20240101000000'",
                "default": "20240101000000"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间，格式如'20241231150000'",
                "default": "20241231150000"
            },
            "count": {
                "type": "integer",
                "description": "数据条数，-1表示全部",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权类型",
                "default": "front_ratio"
            },
            "output_type": {
                "type": "string",
                "description": "输出类型: 'interactive'(交互式HTML), 'static'(静态图片), 'data'(仅数据)",
                "default": "interactive"
            },
            "save_path": {
                "type": "string",
                "description": "保存文件的目录，不提供则使用临时目录",
                "default": ""
            },
            "auto_open": {
                "type": "boolean",
                "description": "是否自动打开生成的文件",
                "default": True
            }
        }
    }
)
async def run_backtest(
    stock_code: str,
    signal: str,
    period: str = "1d",
    start_time: str = "20240101000000",
    end_time: str = "20241231150000",
    count: int = -1,
    dividend_type: str = "front_ratio",
    output_type: str = "interactive",
    save_path: str = "",
    auto_open: bool = True
) -> Dict[str, Any]:
    """
    运行股票回测，并根据指定方式展示结果
    
    Args:
        stock_code: 股票代码，如'600050.SH'
        signal: 策略信号代码，包含买卖条件的VBA代码
        period: K线周期，默认'1d'
        start_time: 开始时间，默认'20240101000000'
        end_time: 结束时间，默认'20241231150000'
        count: 数据条数，默认-1表示全部
        dividend_type: 除权类型，默认'front_ratio'
        output_type: 输出类型，'interactive'(交互式HTML),'static'(静态图片),'data'(仅数据)
        save_path: 保存文件的目录，不提供则使用临时目录
        auto_open: 是否自动打开生成的文件
        
    Returns:
        回测结果字典
    """
    import os
    import platform
    import tempfile
    
    print(f"开始回测 {stock_code}，输出类型: {output_type}")
    print(f"系统信息: {platform.system()} {platform.release()}")
    print(f"临时目录: {tempfile.gettempdir()}")
    
    try:
        # 运行回测获取基础结果
        print("正在运行基础回测...")
        result = await run_single_stock_backtest(
            stock_code=stock_code,
            signal=signal,
            period=period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type
        )
        
        if "error" in result:
            print(f"回测出错: {result.get('error')}")
            return {"status": "error", "message": f"回测失败: {result.get('error', '未知错误')}"}
        
        print("回测完成，获取结果成功")
            
        # 检测运行环境
        env_type = _detect_environment()
        print(f"检测到运行环境: {env_type}")
        
        # 根据输出类型处理
        if output_type.lower() == "data":
            # 仅返回数据
            print("仅返回数据，不生成图表")
            return {
                "status": "success",
                "message": "回测数据已生成",
                "result": result
            }
            
        elif output_type.lower() == "static":
            # 生成静态图表
            print("生成静态图表...")
            
            # 首先尝试在IPython环境中显示
            if env_type in ["ipython", "jupyter", "colab"]:
                try:
                    print("尝试在IPython环境中直接显示...")
                    visual_result = visualize_backtest_result(result)
                    display_backtest_result(visual_result)
                    
                    # 如果不需要保存，直接返回
                    if not save_path and not auto_open:
                        return {
                            "status": "success",
                            "message": "回测结果已在当前环境中直接显示",
                            "summary": result.get("summary", {})
                        }
                except Exception as e:
                    print(f"IPython显示失败: {str(e)}，将尝试保存为文件")
            
            # 创建文件名和保存路径
            file_name = f"回测_{stock_code}_{start_time[:8]}_{end_time[:8]}"
            file_path = _get_safe_file_path(save_path, file_name, "html")
            
            # 生成静态图表并保存为HTML
            try:
                print("生成图表并保存为HTML...")
                visual_result = visualize_backtest_result(result)
                save_backtest_result_to_html(visual_result, file_path)
                print(f"HTML文件已保存到: {file_path}")
            except Exception as e:
                print(f"保存HTML失败: {str(e)}")
                return {"status": "error", "message": f"生成图表失败: {str(e)}"}
            
            # 尝试打开文件
            opened = False
            if auto_open:
                print("尝试打开保存的HTML文件...")
                opened = _open_file(file_path)
            else:
                print("自动打开已禁用，不打开文件")
                
            return {
                "status": "success" if opened else "partial_success",
                "message": f"静态回测图表已保存到: {os.path.abspath(file_path)}" + 
                          ("，并已自动打开" if opened else "，请手动打开此文件"),
                "file_path": os.path.abspath(file_path),
                "summary": result.get("summary", {})
            }
            
        else:  # interactive作为默认选项
            print("生成交互式图表...")
            # 创建文件名和保存路径
            file_name = f"回测_{stock_code}_{start_time[:8]}_{end_time[:8]}"
            file_path = _get_safe_file_path(save_path, file_name, "html")
            
            # 创建交互式图表
            try:
                print("创建交互式HTML内容...")
                interactive_result = create_interactive_html_chart(result, include_plotly=True)
                
                if "error" in interactive_result:
                    print(f"创建交互式图表失败: {interactive_result.get('error')}")
                    return {"status": "error", "message": interactive_result["error"]}
                
                # 保存HTML文件
                print(f"保存到文件: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(interactive_result["interactive_chart"]["html"])
                print(f"HTML文件已保存，大小: {os.path.getsize(file_path)} 字节")
            except Exception as e:
                print(f"保存交互式图表失败: {str(e)}")
                return {"status": "error", "message": f"保存图表失败: {str(e)}"}
            
            # 尝试打开文件
            opened = False
            if auto_open:
                print("尝试打开保存的HTML文件...")
                opened = _open_file(file_path)
            else:
                print("自动打开已禁用，不打开文件")
            
            # 获取更友好的绝对路径显示
            abs_path = os.path.abspath(file_path)
            
            return {
                "status": "success" if opened else "partial_success",
                "message": f"交互式回测图表已保存到:\n{abs_path}" + 
                          ("\n\n并已自动打开浏览器显示。" if opened else "\n\n但自动打开失败，请手动打开此文件查看。"),
                "file_path": abs_path,
                "summary": result.get("summary", {})
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"运行回测时发生异常: {str(e)}")
        print(f"错误详情: {error_details}")
        return {"status": "error", "message": f"运行回测失败: {str(e)}"}

def create_interactive_html_chart(result: Dict[str, Any], include_plotly: bool = True) -> Dict[str, Any]:
    """
    创建交互式HTML图表
    
    Args:
        result: 回测结果字典
        include_plotly: 是否包含plotly.js库代码
        
    Returns:
        包含HTML的字典
    """
    try:
        if "daily_data" not in result or not result["daily_data"]:
            return {**result, "error": "缺少数据无法创建交互式图表"}
        
        import json
        from datetime import datetime
        
        # 提取数据
        daily_data = result["daily_data"]
        
        # 准备JSON数据
        chart_data = {
            "dates": [],
            "strategy_values": [],
            "drawdowns": [],
            "holdings": []
        }
        
        for day in daily_data:
            date_str = day.get("date")
            if isinstance(date_str, datetime):
                date_str = date_str.strftime("%Y-%m-%d")
            
            chart_data["dates"].append(date_str)
            chart_data["strategy_values"].append(day.get("strategy_value", 0))
            chart_data["drawdowns"].append(day.get("drawdown", 0))
            chart_data["holdings"].append(day.get("holding_period", 0) > 0)
        
        # 准备汇总数据
        summary = result.get("summary", {})
        params = result.get("parameters", {})
        
        # 构建HTML
        plotly_js = """
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        """ if include_plotly else ""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>交互式回测图表 - {params.get("stock_code", "")}</title>
            {plotly_js}
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                }}
                h1 {{
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .stats-container {{
                    display: flex;
                    flex-wrap: wrap;
                    margin-bottom: 20px;
                }}
                .stat-card {{
                    flex: 1;
                    min-width: 150px;
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin: 5px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #0066cc;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #666;
                    margin-top: 5px;
                }}
                .charts-container {{
                    display: flex;
                    flex-direction: column;
                    height: 600px;
                }}
                #strategy-chart {{
                    flex: 3;
                }}
                #drawdown-chart {{
                    flex: 1;
                    margin-top: 15px;
                }}
                .param-row {{
                    display: flex;
                    margin-bottom: 10px;
                }}
                .param-label {{
                    font-weight: bold;
                    width: 120px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>策略回测结果 - {params.get("stock_code", "")}</h1>
                
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-value">{summary.get("总收益率", 0):.2f}%</div>
                        <div class="stat-label">总收益率</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get("最大回撤", 0):.2f}%</div>
                        <div class="stat-label">最大回撤</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get("胜率", 0):.2f}</div>
                        <div class="stat-label">胜率</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get("交易次数", 0)}</div>
                        <div class="stat-label">交易次数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get("收益回撤比", 0):.2f}</div>
                        <div class="stat-label">收益回撤比</div>
                    </div>
                </div>
                
                <div class="param-row">
                    <div class="param-label">股票代码:</div>
                    <div>{params.get("stock_code", "")}</div>
                </div>
                <div class="param-row">
                    <div class="param-label">K线周期:</div>
                    <div>{params.get("period", "")}</div>
                </div>
                <div class="param-row">
                    <div class="param-label">回测区间:</div>
                    <div>{params.get("start_time", "").replace("000000", "")} 至 {params.get("end_time", "").replace("150000", "")}</div>
                </div>
                
                <div class="charts-container">
                    <div id="strategy-chart"></div>
                    <div id="drawdown-chart"></div>
                </div>
            </div>
            
            <script>
                // 图表数据
                const chartData = {json.dumps(chart_data)};
                
                // 策略收益图表
                const strategyTrace = {{
                    x: chartData.dates,
                    y: chartData.strategy_values,
                    type: 'scatter',
                    mode: 'lines',
                    name: '策略收益率(%)',
                    line: {{ color: 'rgb(0, 102, 204)', width: 2 }}
                }};
                
                // 持仓区间
                const holdingShapes = [];
                let inHolding = chartData.holdings[0];
                let startIdx = inHolding ? 0 : null;
                
                for (let i = 1; i < chartData.holdings.length; i++) {{
                    if (chartData.holdings[i] && !inHolding) {{
                        startIdx = i;
                        inHolding = true;
                    }} else if (!chartData.holdings[i] && inHolding) {{
                        holdingShapes.push({{
                            type: 'rect',
                            xref: 'x',
                            yref: 'paper',
                            x0: chartData.dates[startIdx],
                            y0: 0,
                            x1: chartData.dates[i-1],
                            y1: 1,
                            fillcolor: 'rgba(0, 128, 0, 0.1)',
                            line: {{ width: 0 }}
                        }});
                        inHolding = false;
                    }}
                }}
                
                // 如果最后是持仓状态
                if (inHolding) {{
                    holdingShapes.push({{
                        type: 'rect',
                        xref: 'x',
                        yref: 'paper',
                        x0: chartData.dates[startIdx],
                        y0: 0,
                        x1: chartData.dates[chartData.dates.length-1],
                        y1: 1,
                        fillcolor: 'rgba(0, 128, 0, 0.1)',
                        line: {{ width: 0 }}
                    }});
                }}
                
                const strategyLayout = {{
                    title: '策略收益曲线',
                    xaxis: {{ title: '日期' }},
                    yaxis: {{ title: '收益率(%)' }},
                    shapes: holdingShapes,
                    hovermode: 'closest',
                    margin: {{ t: 40, b: 40, l: 60, r: 40 }}
                }};
                
                // 回撤图表
                const drawdownTrace = {{
                    x: chartData.dates,
                    y: chartData.drawdowns,
                    type: 'scatter',
                    fill: 'tozeroy',
                    fillcolor: 'rgba(255, 0, 0, 0.3)',
                    line: {{ color: 'rgb(255, 0, 0)' }},
                    name: '回撤(%)'
                }};
                
                const drawdownLayout = {{
                    title: '回撤曲线',
                    xaxis: {{ title: '日期' }},
                    yaxis: {{ title: '回撤(%)', autorange: 'reversed' }},
                    margin: {{ t: 40, b: 40, l: 60, r: 40 }}
                }};
                
                // 绘制图表
                Plotly.newPlot('strategy-chart', [strategyTrace], strategyLayout);
                Plotly.newPlot('drawdown-chart', [drawdownTrace], drawdownLayout);
            </script>
        </body>
        </html>
        """
        
        return {
            **result,
            "interactive_chart": {
                "html": html,
                "chart_data": chart_data
            }
        }
        
    except Exception as e:
        return {**result, "error": f"创建交互式图表失败: {str(e)}"}

@tool_registry.register(
    name="display_backtest_chart",
    description="直接显示回测结果图表，不返回数据",
    input_schema={
        "type": "object",
        "required": ["stock_code", "signal"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600050.SH'"
            },
            "signal": {
                "type": "string",
                "description": "策略信号代码，包含买卖条件的VBA代码"
            },
            "period": {
                "type": "string",
                "description": "K线周期",
                "default": "1d"
            },
            "start_time": {
                "type": "string",
                "description": "开始时间，格式如'20240101000000'",
                "default": "20240101000000"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间，格式如'20241231150000'",
                "default": "20241231150000"
            },
            "count": {
                "type": "integer",
                "description": "数据条数，-1表示全部",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权类型",
                "default": "front_ratio"
            },
            "temp_html_path": {
                "type": "string",
                "description": "临时HTML文件保存路径，不提供则使用系统临时目录",
                "default": ""
            }
        }
    }
)
async def display_backtest_chart(
    stock_code: str,
    signal: str,
    period: str = "1d",
    start_time: str = "20240101000000",
    end_time: str = "20241231150000",
    count: int = -1,
    dividend_type: str = "front_ratio",
    temp_html_path: str = ""
) -> Dict[str, Any]:
    """
    运行单个股票的策略回测并直接显示图表（不返回数据）
    
    Args:
        stock_code: 股票代码，如'600050.SH'
        signal: 策略信号代码，包含买卖条件的VBA代码
        period: K线周期，默认'1d'
        start_time: 开始时间，默认'20240101000000'
        end_time: 结束时间，默认'20241231150000'
        count: 数据条数，默认-1表示全部
        dividend_type: 除权类型，默认'front_ratio'
        temp_html_path: 临时HTML文件保存路径，不提供则使用系统临时目录
    
    Returns:
        操作结果字典
    """
    # 使用新函数实现
    return await run_backtest(
        stock_code=stock_code,
        signal=signal,
        period=period,
        start_time=start_time,
        end_time=end_time,
        count=count,
        dividend_type=dividend_type,
        output_type="interactive",
        save_path=temp_html_path,
        auto_open=True
    )

@tool_registry.register(
    name="save_interactive_backtest_chart",
    description="保存并显示交互式回测图表",
    input_schema={
        "type": "object",
        "required": ["stock_code", "signal"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600050.SH'"
            },
            "signal": {
                "type": "string",
                "description": "策略信号代码，包含买卖条件的VBA代码"
            },
            "period": {
                "type": "string",
                "description": "K线周期",
                "default": "1d"
            },
            "start_time": {
                "type": "string",
                "description": "开始时间，格式如'20240101000000'",
                "default": "20240101000000"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间，格式如'20241231150000'",
                "default": "20241231150000"
            },
            "count": {
                "type": "integer",
                "description": "数据条数，-1表示全部",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权类型",
                "default": "front_ratio"
            },
            "html_path": {
                "type": "string",
                "description": "HTML文件保存路径，不提供则使用系统临时目录",
                "default": ""
            },
            "include_plotly": {
                "type": "boolean",
                "description": "是否在HTML中包含plotly.js库（离线使用）",
                "default": True
            }
        }
    }
)
async def save_interactive_backtest_chart(
    stock_code: str,
    signal: str,
    period: str = "1d",
    start_time: str = "20240101000000",
    end_time: str = "20241231150000",
    count: int = -1,
    dividend_type: str = "front_ratio",
    html_path: str = "",
    include_plotly: bool = True
) -> Dict[str, Any]:
    """
    运行回测并保存交互式HTML图表
    
    Args:
        stock_code: 股票代码，如'600050.SH'
        signal: 策略信号代码，包含买卖条件的VBA代码
        period: K线周期，默认'1d'
        start_time: 开始时间，默认'20240101000000'
        end_time: 结束时间，默认'20241231150000'
        count: 数据条数，默认-1表示全部
        dividend_type: 除权类型，默认'front_ratio'
        html_path: HTML文件保存路径，不提供则使用系统临时目录
        include_plotly: 是否在HTML中包含plotly.js库
        
    Returns:
        操作结果字典
    """
    # 使用新函数实现
    return await run_backtest(
        stock_code=stock_code,
        signal=signal,
        period=period,
        start_time=start_time,
        end_time=end_time,
        count=count,
        dividend_type=dividend_type,
        output_type="interactive",
        save_path=html_path,
        auto_open=True
    )

# 不需要view_backtest_results函数了，功能已合并到run_backtest
# 删除view_backtest_results函数的注册，改为别名
tool_registry.register(
    name="view_backtest_results",
    description="直接显示美观的股票回测结果",
    input_schema={
        "type": "object",
        "required": ["stock_code", "signal"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600050.SH'"
            },
            "signal": {
                "type": "string",
                "description": "策略信号代码，包含买卖条件的VBA代码"
            },
            "period": {
                "type": "string",
                "description": "K线周期",
                "default": "1d"
            },
            "start_time": {
                "type": "string",
                "description": "开始时间，格式如'20240101000000'",
                "default": "20240101000000"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间，格式如'20241231150000'",
                "default": "20241231150000"
            },
            "count": {
                "type": "integer",
                "description": "数据条数，-1表示全部",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权类型",
                "default": "front_ratio"
            }
        }
    }
)(run_backtest)  # 将view_backtest_results设为run_backtest的别名