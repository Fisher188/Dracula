from typing import List, Any, Dict, Literal, Optional, Union, Tuple
from ..registry import tool_registry
import xtquant.xttrader as xttrader
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import xtquant.xtdata as xtdata
import time
import datetime
import traceback
import os

class TradeDetailData:
    """交易数据结构，用于存储持仓或账户信息"""
    def __init__(self, data_dict: Dict = None):
        # 持仓数据字段
        self.m_strInstrumentID = ""        # 股票代码
        self.m_strExchangeID = ""          # 市场类型
        self.m_strInstrumentName = ""      # 证券名称
        self.m_nVolume = 0                 # 持仓量
        self.m_nCanUseVolume = 0           # 可用数量
        self.m_dOpenPrice = 0.0            # 成本价
        self.m_dInstrumentValue = 0.0      # 市值
        self.m_dPositionCost = 0.0         # 持仓成本
        self.m_dPositionProfit = 0.0       # 盈亏
        
        # 账户数据字段
        self.m_dBalance = 0.0              # 总资产
        self.m_dAssureAsset = 0.0          # 净资产
        self.m_dInstrumentValue = 0.0      # 总市值
        self.m_dTotalDebit = 0.0           # 总负债
        self.m_dAvailable = 0.0            # 可用金额
        self.m_dPositionProfit = 0.0       # 盈亏
        self.m_dCash = 0.0                 # 现金
        
        # 如果传入数据字典，则初始化对象
        if data_dict:
            for key, value in data_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)


# 全局交易实例
_trader_instance = None
_callback_instance = None
_session_id = None


class XtQuantTraderCallbackImpl(XtQuantTraderCallback):
    """量化交易回调实现类"""
    
    def __init__(self):
        super().__init__()
        self.order_callbacks = {}
        self.trade_callbacks = {}
        self.error_callbacks = {}
        
    def on_disconnected(self):
        """连接断开回调"""
        print(f"{datetime.datetime.now()} 连接断开回调")

    def on_stock_order(self, order):
        """委托回报推送"""
        print(f"{datetime.datetime.now()} 委托回调 投资备注: {order.order_remark}")
        
        # 执行回调函数（如果有）
        order_id = order.order_id
        if order_id in self.order_callbacks:
            self.order_callbacks[order_id](order)
            
    def on_stock_trade(self, trade):
        """成交变动推送"""
        print(f"{datetime.datetime.now()} 成交回调 {trade.order_remark} "
              f"委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} "
              f"成交数量 {trade.traded_volume}")
        
        # 执行回调函数（如果有）
        order_id = trade.order_id
        if order_id in self.trade_callbacks:
            self.trade_callbacks[order_id](trade)

    def on_order_error(self, order_error):
        """委托失败推送"""
        print(f"委托报错回调 {order_error.order_remark} {order_error.error_msg}")
        
        # 执行回调函数（如果有）
        order_id = order_error.order_id
        if order_id in self.error_callbacks:
            self.error_callbacks[order_id](order_error)

    def on_cancel_error(self, cancel_error):
        """撤单失败推送"""
        print(f"{datetime.datetime.now()} 撤单失败: {cancel_error.error_msg}")

    def on_order_stock_async_response(self, response):
        """异步下单回报推送"""
        print(f"异步委托回调 投资备注: {response.order_remark}")

    def on_cancel_order_stock_async_response(self, response):
        """异步撤单回报推送"""
        print(f"{datetime.datetime.now()} 异步撤单回调: {response.cancel_result}")

    def on_account_status(self, status):
        """账户状态推送"""
        print(f"{datetime.datetime.now()} 账户状态变更: {status.account_id}, 状态: {status.status}")
        
    def register_order_callback(self, order_id, callback):
        """注册委托回调函数"""
        self.order_callbacks[order_id] = callback
        
    def register_trade_callback(self, order_id, callback):
        """注册成交回调函数"""
        self.trade_callbacks[order_id] = callback
        
    def register_error_callback(self, order_id, callback):
        """注册错误回调函数"""
        self.error_callbacks[order_id] = callback


def get_trader_instance() -> XtQuantTrader:
    """获取交易实例（单例模式）"""
    global _trader_instance, _callback_instance, _session_id
    
    if _trader_instance is None:
        # 尝试从文件读取自定义路径
        path = r'C:\Program Files\821\迅投极速交易终端睿智融科版\userdata'
        try:
            if os.path.exists("trader_path.txt"):
                with open("trader_path.txt", "r") as f:
                    custom_path = f.read().strip()
                    if custom_path:
                        path = custom_path
        except:
            pass
            
        print(f"正在使用交易路径: {path}")
        
        # 生成session id
        _session_id = int(time.time())
        print(f"生成会话ID: {_session_id}")
        
        # 创建交易实例
        _trader_instance = XtQuantTrader(path, _session_id)
        
        # 创建回调实例
        _callback_instance = XtQuantTraderCallbackImpl()
        _trader_instance.register_callback(_callback_instance)
        
        # 启动交易线程
        _trader_instance.start()
        print("交易线程已启动")
        
    return _trader_instance


def get_callback_instance() -> XtQuantTraderCallbackImpl:
    """获取回调实例"""
    global _callback_instance
    
    if _callback_instance is None:
        # 确保已创建交易实例
        get_trader_instance()
    
    return _callback_instance


def connect_trader(account_id: str, account_type: str = 'STOCK') -> bool:
    """
    连接交易服务器并订阅账户
    
    Args:
        account_id: 账户ID
        account_type: 账户类型，'STOCK'表示股票账户，'CREDIT'表示信用账户，'FUTURE'表示期货账户
    
    Returns:
        连接是否成功
    """
    trader = get_trader_instance()
    
    # 创建账户对象
    account = StockAccount(account_id, account_type)
    
    # 建立交易连接
    connect_result = trader.connect()
    if connect_result != 0:
        print(f"连接交易服务器失败，错误码: {connect_result}")
        return False
    
    # 订阅账户
    subscribe_result = trader.subscribe(account)
    if subscribe_result != 0:
        print(f"订阅账户失败，错误码: {subscribe_result}")
        return False
    
    print(f"成功连接并订阅账户: {account_id}")
    return True


def get_trade_detail_data(account: str, market_type: str, query_type: str) -> List[TradeDetailData]:
    """
    获取账户相关信息，包括持仓信息和账户资金信息
    
    Args:
        account: 账户ID，如'123456'
        market_type: 市场类型，如'stock'表示股票市场
        query_type: 查询类型，'position'表示查询持仓，'account'表示查询账户资金
    
    Returns:
        包含账户相关信息的TradeDetailData对象列表
    """
    result = []
    
    try:
        print(f"开始查询账户: {account}, 市场类型: {market_type}, 查询类型: {query_type}")
        
        # 获取交易实例
        trader = get_trader_instance()
        
        # 创建账户对象
        acc = StockAccount(account, market_type.upper())
        print(f"创建账户对象: {acc.account_id}, 类型: {acc.account_type}")
        
        # 建立交易连接
        connect_result = trader.connect()
        print(f"连接交易服务器结果: {connect_result}")
        if connect_result != 0:
            print(f"连接交易服务器失败，错误码: {connect_result}")
            return result
        
        # 订阅账户
        subscribe_result = trader.subscribe(acc)
        print(f"订阅账户结果: {subscribe_result}")
        if subscribe_result != 0:
            print(f"订阅账户失败，错误码: {subscribe_result}")
            return result
        
        print(f"成功连接并订阅账户: {account}")
        
        # 尝试通过更简单的方式获取一下账户信息，确认基本连接是否正常
        try:
            print(f"测试获取账户资产是否正常...")
            test_account_info = trader.query_stock_asset(acc)
            if test_account_info:
                print(f"账户基本信息获取成功: {test_account_info}")
            else:
                print(f"测试获取账户资产返回空值，请检查账户ID是否有效")
        except Exception as e:
            print(f"测试获取账户资产失败: {str(e)}")
            traceback.print_exc()
        
        if query_type.lower() == 'position':
            # 查询持仓信息
            print(f"开始查询持仓信息...")
            positions = trader.query_stock_positions(acc)
            
            print(f"查询到持仓记录数: {len(positions)}")
            if len(positions) > 0:
                print(f"第一条持仓记录: {positions[0]}")
            
            for pos in positions:
                # 转换为TradeDetailData对象
                data = TradeDetailData()
                data.m_strInstrumentID = pos.stock_code
                data.m_strExchangeID = pos.stock_code.split('.')[-1] if '.' in pos.stock_code else ''
                
                # 尝试获取证券名称，如果失败则留空
                try:
                    instrument_detail = xtdata.get_instrument_detail(pos.stock_code)
                    data.m_strInstrumentName = instrument_detail.get('InstrumentName', '')
                except Exception as e:
                    print(f"获取证券名称失败: {e}")
                    data.m_strInstrumentName = ''
                
                # 安全访问持仓字段
                if hasattr(pos, 'm_nVolume'):
                    data.m_nVolume = pos.m_nVolume
                elif hasattr(pos, 'volume'):
                    data.m_nVolume = pos.volume
                
                if hasattr(pos, 'm_nCanUseVolume'):
                    data.m_nCanUseVolume = pos.m_nCanUseVolume
                elif hasattr(pos, 'can_use_volume'):
                    data.m_nCanUseVolume = pos.can_use_volume
                
                if hasattr(pos, 'm_dOpenPrice'):
                    data.m_dOpenPrice = pos.m_dOpenPrice
                elif hasattr(pos, 'open_price'):
                    data.m_dOpenPrice = pos.open_price
                
                if hasattr(pos, 'm_dMarketValue'):
                    data.m_dInstrumentValue = pos.m_dMarketValue
                elif hasattr(pos, 'market_value'):
                    data.m_dInstrumentValue = pos.market_value
                
                if hasattr(pos, 'm_dPositionCost'):
                    data.m_dPositionCost = pos.m_dPositionCost
                elif hasattr(pos, 'position_cost'):
                    data.m_dPositionCost = pos.position_cost
                
                if hasattr(pos, 'm_dPositionProfit'):
                    data.m_dPositionProfit = pos.m_dPositionProfit
                elif hasattr(pos, 'position_profit'):
                    data.m_dPositionProfit = pos.position_profit
                
                result.append(data)
                
        elif query_type.lower() == 'account':
            # 查询账户资金信息
            print(f"开始查询账户资金信息...")
            account_info = trader.query_stock_asset(acc)
            
            if account_info:
                print(f"账户资金信息: {account_info}")
                data = TradeDetailData()
                
                # 安全访问账户资金字段
                # 总资产
                if hasattr(account_info, 'm_dBalance'):
                    data.m_dBalance = account_info.m_dBalance
                elif hasattr(account_info, 'balance'):
                    data.m_dBalance = account_info.balance
                
                # 净资产
                if hasattr(account_info, 'm_dAssureAsset'):
                    data.m_dAssureAsset = account_info.m_dAssureAsset
                elif hasattr(account_info, 'assure_asset'):
                    data.m_dAssureAsset = account_info.assure_asset
                
                # 总市值
                if hasattr(account_info, 'm_dMarketValue'):
                    data.m_dInstrumentValue = account_info.m_dMarketValue
                elif hasattr(account_info, 'market_value'):
                    data.m_dInstrumentValue = account_info.market_value
                
                # 总负债
                if hasattr(account_info, 'm_dTotalDebit'):
                    data.m_dTotalDebit = account_info.m_dTotalDebit
                elif hasattr(account_info, 'total_debit'):
                    data.m_dTotalDebit = account_info.total_debit
                
                # 可用金额
                if hasattr(account_info, 'm_dAvailable'):
                    data.m_dAvailable = account_info.m_dAvailable
                elif hasattr(account_info, 'available'):
                    data.m_dAvailable = account_info.available
                
                # 盈亏
                if hasattr(account_info, 'm_dPositionProfit'):
                    data.m_dPositionProfit = account_info.m_dPositionProfit
                elif hasattr(account_info, 'position_profit'):
                    data.m_dPositionProfit = account_info.position_profit
                
                # 现金
                if hasattr(account_info, 'm_dCash'):
                    data.m_dCash = account_info.m_dCash
                elif hasattr(account_info, 'cash'):
                    data.m_dCash = account_info.cash
                
                print(f"查询到账户资金信息: 总资产={data.m_dBalance}, 可用金额={data.m_dAvailable}, 现金={data.m_dCash}")
                result.append(data)
            else:
                print(f"未查询到账户 {account} 资金信息，返回None")
                
                # 不再尝试列出所有可用账户，因为API不支持
                print("无法获取所有可用账户，XtQuantTrader对象没有query_stock_account方法")
    except Exception as e:
        print(f"获取交易数据出错: {str(e)}")
        traceback.print_exc()
        
    return result


def place_order(account_id: str, stock_code: str, direction: str, volume: int,
                price_type: str = 'LATEST', price: float = -1, 
                strategy_name: str = '', remark: str = '') -> str:
    """
    下单函数
    
    Args:
        account_id: 账户ID
        stock_code: 股票代码
        direction: 交易方向，'BUY'或'SELL'
        volume: 交易数量
        price_type: 价格类型，'LATEST'表示市价，'FIX'表示限价
        price: 价格，仅在限价委托时有效
        strategy_name: 策略名称
        remark: 投资备注
    
    Returns:
        委托编号
    """
    trader = get_trader_instance()
    
    # 创建账户对象
    acc = StockAccount(account_id, 'STOCK')
    
    # 确保已连接并已订阅
    connect_trader(account_id, 'STOCK')
    
    # 设置交易方向
    if direction.upper() == 'BUY':
        direction_code = xtconstant.STOCK_BUY
    elif direction.upper() == 'SELL':
        direction_code = xtconstant.STOCK_SELL
    else:
        raise ValueError(f"不支持的交易方向: {direction}")
    
    # 设置价格类型
    if price_type.upper() == 'LATEST':
        price_type_code = xtconstant.LATEST_PRICE
    elif price_type.upper() == 'FIX':
        price_type_code = xtconstant.FIX_PRICE
    else:
        raise ValueError(f"不支持的价格类型: {price_type}")
    
    # 下单
    order_id = trader.order_stock_async(acc, stock_code, direction_code, volume, 
                                        price_type_code, price, strategy_name, remark)
    
    return order_id


def calculate_buy_volume(stock_code: str, amount: float) -> int:
    """
    计算可买入的股票数量
    
    Args:
        stock_code: 股票代码
        amount: 目标买入金额
    
    Returns:
        可买入的股票数量，按100股整数倍计算
    """
    # 获取最新行情
    full_tick = xtdata.get_full_tick([stock_code])
    if stock_code not in full_tick:
        raise ValueError(f"获取股票 {stock_code} 行情失败")
    
    # 获取最新价格
    latest_price = full_tick[stock_code]['lastPrice']
    
    # 计算可买入数量，取整为100的整数倍
    volume = int(amount / latest_price / 100) * 100
    
    return volume


@tool_registry.register(
    name="connect_account",
    description="连接并订阅账户",
    input_schema={
        "type": "object",
        "required": ["account"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "market_type": {
                "type": "string",
                "description": "市场类型，如'stock'表示股票市场",
                "default": "stock"
            },
            "path": {
                "type": "string",
                "description": "交易路径，不提供则使用默认值",
                "default": ""
            }
        }
    }
)
async def connect_account(account: str, market_type: str = "stock", path: str = "") -> Dict:
    """
    连接并订阅账户
    
    Args:
        account: 账户ID
        market_type: 市场类型，如'stock'表示股票市场
        path: 交易路径，不提供则使用默认值
    
    Returns:
        连接结果字典
    """
    try:
        global _trader_instance
        
        print(f"开始连接账户: {account}, 市场类型: {market_type}")
        
        # 如果提供了自定义路径，重新初始化交易实例
        if path and _trader_instance is not None:
            print(f"提供了自定义路径: {path}，重新初始化交易实例")
            # 关闭旧的交易实例
            _trader_instance.stop()
            _trader_instance = None
        
        # 如果提供了自定义路径，覆盖默认路径
        if path:
            # 保存路径到临时文件，以便后续使用
            with open("trader_path.txt", "w") as f:
                f.write(path)
        
        # 获取交易实例
        trader = get_trader_instance()
        
        # 创建账户对象
        acc = StockAccount(account, market_type.upper())
        print(f"创建账户对象: {acc.account_id}, 类型: {acc.account_type}")
        
        # 建立交易连接
        connect_result = trader.connect()
        print(f"连接交易服务器结果: {connect_result}")
        if connect_result != 0:
            print(f"连接交易服务器失败，错误码: {connect_result}")
            return {
                "success": False,
                "message": f"连接交易服务器失败，错误码: {connect_result}",
                "account": account,
                "market_type": market_type
            }
        
        # 订阅账户
        subscribe_result = trader.subscribe(acc)
        print(f"订阅账户结果: {subscribe_result}")
        if subscribe_result != 0:
            print(f"订阅账户失败，错误码: {subscribe_result}")
            return {
                "success": False,
                "message": f"订阅账户失败，错误码: {subscribe_result}",
                "account": account,
                "market_type": market_type
            }
        
        print(f"成功连接并订阅账户: {account}")
        
        # 尝试检查是否能获取账户信息
        try:
            test_account_info = trader.query_stock_asset(acc)
            if test_account_info:
                print(f"成功获取账户基本信息: {test_account_info}")
                
                # 检查account_info对象的属性并安全访问
                balance = getattr(test_account_info, 'balance', 0.0)
                if hasattr(test_account_info, 'm_dBalance'):
                    balance = test_account_info.m_dBalance
                
                available = getattr(test_account_info, 'available', 0.0) 
                if hasattr(test_account_info, 'm_dAvailable'):
                    available = test_account_info.m_dAvailable
                
                cash = getattr(test_account_info, 'cash', 0.0)
                if hasattr(test_account_info, 'm_dCash'):
                    cash = test_account_info.m_dCash
                
                return {
                    "success": True,
                    "message": f"成功连接并订阅账户: {account}",
                    "account": account,
                    "market_type": market_type,
                    "balance": balance,
                    "available": available,
                    "cash": cash
                }
            else:
                print(f"账户 {account} 不存在或未登录")
                return {
                    "success": False,
                    "message": f"账户 {account} 不存在或未登录",
                    "account": account,
                    "market_type": market_type
                }
        except Exception as e:
            print(f"测试账户连接失败: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"测试账户连接失败: {str(e)}",
                "account": account,
                "market_type": market_type,
                "error_type": str(type(e).__name__)
            }
    
    except Exception as e:
        print(f"连接账户出错: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"连接账户出错: {str(e)}",
            "account": account,
            "market_type": market_type,
            "error_type": str(type(e).__name__)
        }


@tool_registry.register(
    name="get_account_positions",
    description="获取账户持仓信息",
    input_schema={
        "type": "object",
        "required": ["account"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "market_type": {
                "type": "string",
                "description": "市场类型，如'stock'表示股票市场",
                "default": "stock"
            }
        }
    }
)
async def get_account_positions(account: str, market_type: str = "stock") -> Dict:
    """
    获取账户持仓信息
    
    Args:
        account: 账户ID，如'123456'
        market_type: 市场类型，如'stock'表示股票市场
    
    Returns:
        包含持仓信息或错误信息的字典
    """
    try:
        print(f"开始获取账户 {account} 的持仓信息")
        
        # 获取交易实例
        trader = get_trader_instance()
        
        # 创建账户对象
        acc = StockAccount(account, market_type.upper())
        
        # 查询持仓信息
        try:
            print(f"开始查询持仓信息...")
            positions = trader.query_stock_positions(acc)
            
            print(f"查询到持仓记录数: {len(positions)}")
            if len(positions) > 0:
                print(f"第一条持仓记录: {positions[0]}")
                
            # 将查询结果转换为字典列表
            positions_list = []
            for pos in positions:
                # 尝试获取证券名称，如果失败则留空
                stock_name = ""
                try:
                    instrument_detail = xtdata.get_instrument_detail(pos.stock_code)
                    stock_name = instrument_detail.get('InstrumentName', '')
                except Exception as e:
                    print(f"获取证券名称失败: {e}")
                
                # 安全地获取持仓属性
                pos_dict = {
                    'stock_code': getattr(pos, 'stock_code', ''),
                    'stock_name': stock_name,
                    'exchange': getattr(pos, 'stock_code', '').split('.')[-1] if '.' in getattr(pos, 'stock_code', '') else ''
                }
                
                # 安全获取持仓量和可用数量
                if hasattr(pos, 'm_nVolume'):
                    pos_dict['volume'] = pos.m_nVolume
                elif hasattr(pos, 'volume'):
                    pos_dict['volume'] = pos.volume
                else:
                    pos_dict['volume'] = 0
                
                if hasattr(pos, 'm_nCanUseVolume'):
                    pos_dict['available_volume'] = pos.m_nCanUseVolume
                elif hasattr(pos, 'can_use_volume'):
                    pos_dict['available_volume'] = pos.can_use_volume
                else:
                    pos_dict['available_volume'] = 0
                
                # 安全获取成本价
                if hasattr(pos, 'm_dOpenPrice'):
                    pos_dict['open_price'] = pos.m_dOpenPrice
                elif hasattr(pos, 'open_price'):
                    pos_dict['open_price'] = pos.open_price
                else:
                    pos_dict['open_price'] = 0.0
                
                # 安全获取市值
                if hasattr(pos, 'm_dMarketValue'):
                    pos_dict['market_value'] = pos.m_dMarketValue
                elif hasattr(pos, 'market_value'):
                    pos_dict['market_value'] = pos.market_value
                else:
                    pos_dict['market_value'] = 0.0
                
                # 持仓成本 - 对于股票可能不适用
                if hasattr(pos, 'm_dPositionCost'):
                    pos_dict['position_cost'] = pos.m_dPositionCost
                elif hasattr(pos, 'position_cost'):
                    pos_dict['position_cost'] = pos.position_cost
                elif hasattr(pos, 'm_dTotalCost'):  # 尝试使用累计成本
                    pos_dict['position_cost'] = pos.m_dTotalCost
                elif hasattr(pos, 'total_cost'):
                    pos_dict['position_cost'] = pos.total_cost
                else:
                    # 如果没有持仓成本字段，可以尝试用开仓价乘以持仓量来估算
                    if 'open_price' in pos_dict and 'volume' in pos_dict:
                        pos_dict['position_cost'] = pos_dict['open_price'] * pos_dict['volume']
                    else:
                        pos_dict['position_cost'] = 0.0
                
                # 持仓盈亏 - 对于股票可能不适用
                if hasattr(pos, 'm_dPositionProfit'):
                    pos_dict['position_profit'] = pos.m_dPositionProfit
                elif hasattr(pos, 'position_profit'):
                    pos_dict['position_profit'] = pos.position_profit
                elif hasattr(pos, 'm_dFloatProfit'):  # 尝试使用浮动盈亏
                    pos_dict['position_profit'] = pos.m_dFloatProfit
                elif hasattr(pos, 'float_profit'):
                    pos_dict['position_profit'] = pos.float_profit
                else:
                    pos_dict['position_profit'] = 0.0
                
                # 添加额外有用字段
                if hasattr(pos, 'm_dProfitRate'):
                    pos_dict['profit_rate'] = pos.m_dProfitRate
                elif hasattr(pos, 'profit_rate'):
                    pos_dict['profit_rate'] = pos.profit_rate
                
                if hasattr(pos, 'm_dLastPrice'):
                    pos_dict['last_price'] = pos.m_dLastPrice
                elif hasattr(pos, 'last_price'):
                    pos_dict['last_price'] = pos.last_price
                
                positions_list.append(pos_dict)
            
            # 打印第一个持仓的完整字段列表（如果有），方便调试
            if len(positions) > 0:
                first_pos = positions[0]
                print("持仓对象的可用字段:")
                for attr_name in dir(first_pos):
                    if not attr_name.startswith('__') and not callable(getattr(first_pos, attr_name)):
                        try:
                            attr_value = getattr(first_pos, attr_name)
                            print(f"  {attr_name}: {attr_value}")
                        except:
                            print(f"  {attr_name}: <无法访问>")
            
            return {
                "success": True,
                "message": f"成功获取账户 {account} 的持仓信息",
                "positions": positions_list
            }
        except Exception as e:
            print(f"查询持仓信息失败: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"查询账户 {account} 持仓信息失败: {str(e)}",
                "error_type": str(type(e).__name__),
                "positions": []
            }
    
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取账户 {account} 持仓信息失败: {str(e)}",
            "error_type": str(type(e).__name__),
            "positions": []
        }


@tool_registry.register(
    name="get_account_info",
    description="获取账户资金信息",
    input_schema={
        "type": "object",
        "required": ["account"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "market_type": {
                "type": "string",
                "description": "市场类型，如'stock'表示股票市场",
                "default": "stock"
            }
        }
    }
)
async def get_account_info(account: str, market_type: str = "stock") -> Dict:
    """
    获取账户资金信息
    
    Args:
        account: 账户ID，如'123456'
        market_type: 市场类型，如'stock'表示股票市场
    
    Returns:
        包含账户资金信息或错误信息的字典
    """
    try:
        print(f"开始获取账户 {account} 的资金信息")
        
        # 获取交易实例
        trader = get_trader_instance()
        
        # 创建账户对象
        acc = StockAccount(account, market_type.upper())
        
        # 查询账户资金信息
        try:
            print(f"开始查询账户资金信息...")
            account_info = trader.query_stock_asset(acc)
            
            if account_info:
                print(f"账户资金信息: {account_info}")
                
                # 将查询结果转换为字典，安全访问属性
                acc_info = {}
                
                # 总资产
                if hasattr(account_info, 'm_dBalance'):
                    acc_info['balance'] = account_info.m_dBalance
                elif hasattr(account_info, 'balance'):
                    acc_info['balance'] = account_info.balance
                else:
                    acc_info['balance'] = 0.0
                
                # 净资产
                if hasattr(account_info, 'm_dAssureAsset'):
                    acc_info['net_asset'] = account_info.m_dAssureAsset
                elif hasattr(account_info, 'assure_asset'):
                    acc_info['net_asset'] = account_info.assure_asset
                else:
                    acc_info['net_asset'] = 0.0
                
                # 总市值
                if hasattr(account_info, 'm_dMarketValue'):
                    acc_info['market_value'] = account_info.m_dMarketValue
                elif hasattr(account_info, 'market_value'):
                    acc_info['market_value'] = account_info.market_value
                else:
                    acc_info['market_value'] = 0.0
                
                # 总负债
                if hasattr(account_info, 'm_dTotalDebit'):
                    acc_info['total_debit'] = account_info.m_dTotalDebit
                elif hasattr(account_info, 'total_debit'):
                    acc_info['total_debit'] = account_info.total_debit
                else:
                    acc_info['total_debit'] = 0.0
                
                # 可用金额
                if hasattr(account_info, 'm_dAvailable'):
                    acc_info['available'] = account_info.m_dAvailable
                elif hasattr(account_info, 'available'):
                    acc_info['available'] = account_info.available
                else:
                    acc_info['available'] = 0.0
                
                # 盈亏
                if hasattr(account_info, 'm_dPositionProfit'):
                    acc_info['position_profit'] = account_info.m_dPositionProfit
                elif hasattr(account_info, 'position_profit'):
                    acc_info['position_profit'] = account_info.position_profit
                else:
                    acc_info['position_profit'] = 0.0
                
                # 现金
                if hasattr(account_info, 'm_dCash'):
                    acc_info['cash'] = account_info.m_dCash
                elif hasattr(account_info, 'cash'):
                    acc_info['cash'] = account_info.cash
                else:
                    acc_info['cash'] = 0.0
                
                print(f"查询到账户资金信息: 总资产={acc_info['balance']}, 可用金额={acc_info['available']}, 现金={acc_info['cash']}")
                
                return {
                    "success": True,
                    "message": f"成功获取账户 {account} 的资金信息",
                    "account_info": acc_info
                }
            else:
                print(f"未查询到账户 {account} 资金信息")
                return {
                    "success": False,
                    "message": f"未查询到账户 {account} 资金信息，请先连接账户",
                    "account_info": None
                }
        except Exception as e:
            print(f"查询账户资金信息失败: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"查询账户 {account} 资金信息失败: {str(e)}",
                "error_type": str(type(e).__name__),
                "account_info": None
            }
    
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取账户 {account} 资金信息失败: {str(e)}",
            "error_type": str(type(e).__name__),
            "account_info": None
        }


@tool_registry.register(
    name="buy_stock",
    description="买入股票",
    input_schema={
        "type": "object",
        "required": ["account", "stock_code", "amount"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600000.SH'"
            },
            "amount": {
                "type": "number",
                "description": "买入金额"
            },
            "price_type": {
                "type": "string",
                "description": "价格类型，'LATEST'表示市价，'FIX'表示限价",
                "default": "LATEST" 
            },
            "price": {
                "type": "number",
                "description": "买入价格，仅在限价委托时有效",
                "default": -1
            },
            "strategy_name": {
                "type": "string",
                "description": "策略名称",
                "default": "auto_trade"
            }
        }
    }
)
async def buy_stock(account: str, stock_code: str, amount: float, 
                    price_type: str = "LATEST", price: float = -1,
                    strategy_name: str = "auto_trade") -> Dict:
    """
    买入股票
    
    Args:
        account: 账户ID
        stock_code: 股票代码，如'600000.SH'
        amount: 买入金额
        price_type: 价格类型，'LATEST'表示市价，'FIX'表示限价
        price: 买入价格，仅在限价委托时有效
        strategy_name: 策略名称
    
    Returns:
        买入结果字典
    """
    try:
        # 获取账户资金信息
        accounts = get_trade_detail_data(account, "stock", "account")
        if not accounts:
            return {"success": False, "message": "获取账户资金信息失败"}
        
        # 获取可用资金
        available_cash = accounts[0].m_dAvailable
        
        # 计算实际买入金额，不超过可用资金
        actual_amount = min(amount, available_cash)
        
        # 获取最新行情
        full_tick = xtdata.get_full_tick([stock_code])
        if stock_code not in full_tick:
            return {"success": False, "message": f"获取股票 {stock_code} 行情失败"}
        
        current_price = full_tick[stock_code]['lastPrice']
        
        # 计算买入数量
        buy_vol = calculate_buy_volume(stock_code, actual_amount)
        if buy_vol <= 0:
            return {"success": False, "message": "计算买入数量为0"}
        
        # 买入股票
        if price_type.upper() == "LATEST":
            price = -1
        
        order_id = place_order(account, stock_code, "BUY", buy_vol, 
                               price_type.upper(), price, strategy_name, stock_code)
        
        return {
            "success": True,
            "message": "委托成功",
            "order_id": order_id,
            "stock_code": stock_code,
            "volume": buy_vol,
            "price": current_price,
            "amount": actual_amount,
            "available_cash": available_cash
        }
    
    except Exception as e:
        return {"success": False, "message": f"买入股票失败: {str(e)}"}


@tool_registry.register(
    name="sell_stock",
    description="卖出股票",
    input_schema={
        "type": "object",
        "required": ["account", "stock_code", "volume"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'600000.SH'"
            },
            "volume": {
                "type": "integer",
                "description": "卖出数量"
            },
            "price_type": {
                "type": "string",
                "description": "价格类型，'LATEST'表示市价，'FIX'表示限价",
                "default": "LATEST" 
            },
            "price": {
                "type": "number",
                "description": "卖出价格，仅在限价委托时有效",
                "default": -1
            },
            "strategy_name": {
                "type": "string",
                "description": "策略名称",
                "default": "auto_trade"
            }
        }
    }
)
async def sell_stock(account: str, stock_code: str, volume: int, 
                     price_type: str = "LATEST", price: float = -1,
                     strategy_name: str = "auto_trade") -> Dict:
    """
    卖出股票
    
    Args:
        account: 账户ID
        stock_code: 股票代码，如'600000.SH'
        volume: 卖出数量
        price_type: 价格类型，'LATEST'表示市价，'FIX'表示限价
        price: 卖出价格，仅在限价委托时有效
        strategy_name: 策略名称
    
    Returns:
        卖出结果字典
    """
    try:
        # 获取持仓信息
        positions = get_trade_detail_data(account, "stock", "position")
        
        # 找出对应股票的持仓
        position = None
        for pos in positions:
            if pos.m_strInstrumentID == stock_code:
                position = pos
                break
        
        if not position:
            return {"success": False, "message": f"未持有股票 {stock_code}"}
        
        # 计算实际卖出数量，不超过可用持仓
        actual_volume = min(volume, position.m_nCanUseVolume)
        if actual_volume <= 0:
            return {"success": False, "message": f"股票 {stock_code} 可用数量为0"}
        
        # 获取最新行情
        full_tick = xtdata.get_full_tick([stock_code])
        if stock_code not in full_tick:
            return {"success": False, "message": f"获取股票 {stock_code} 行情失败"}
        
        current_price = full_tick[stock_code]['lastPrice']
        
        # 卖出股票
        if price_type.upper() == "LATEST":
            price = -1
        
        order_id = place_order(account, stock_code, "SELL", actual_volume, 
                               price_type.upper(), price, strategy_name, stock_code)
        
        return {
            "success": True,
            "message": "委托成功",
            "order_id": order_id,
            "stock_code": stock_code,
            "volume": actual_volume,
            "price": current_price,
            "amount": actual_volume * current_price,
            "position_volume": position.m_nVolume,
            "available_volume": position.m_nCanUseVolume
        }
    
    except Exception as e:
        return {"success": False, "message": f"卖出股票失败: {str(e)}"}


@tool_registry.register(
    name="test_account_connection",
    description="测试账户连接",
    input_schema={
        "type": "object",
        "required": ["account"],
        "properties": {
            "account": {
                "type": "string",
                "description": "账户ID"
            },
            "market_type": {
                "type": "string",
                "description": "市场类型，如'stock'表示股票市场",
                "default": "stock"
            }
        }
    }
)
async def test_account_connection(account: str, market_type: str = "stock") -> Dict:
    """
    简单测试账户连接
    
    Args:
        account: 账户ID
        market_type: 市场类型，如'stock'表示股票市场
    
    Returns:
        测试结果字典
    """
    try:
        print(f"开始测试账户连接: {account}, 市场类型: {market_type}")
        
        # 使用预设路径
        path = r'C:\Program Files\821\迅投极速交易终端睿智融科版\userdata'
        
        # 创建新的交易实例（不使用全局实例）
        session_id = int(time.time())
        trader = XtQuantTrader(path, session_id)
        
        # 启动交易线程
        trader.start()
        print(f"交易线程已启动，会话ID: {session_id}")
        
        # 创建账户对象
        acc = StockAccount(account, market_type.upper())
        print(f"创建账户对象: {acc.account_id}, 类型: {acc.account_type}")
        
        # 建立交易连接
        connect_result = trader.connect()
        print(f"连接交易服务器结果: {connect_result}")
        if connect_result != 0:
            trader.stop()
            return {
                "success": False,
                "message": f"连接交易服务器失败，错误码: {connect_result}",
                "account": account,
                "path": path
            }
        
        # 订阅账户
        subscribe_result = trader.subscribe(acc)
        print(f"订阅账户结果: {subscribe_result}")
        if subscribe_result != 0:
            trader.stop()
            return {
                "success": False,
                "message": f"订阅账户失败，错误码: {subscribe_result}",
                "account": account,
                "path": path
            }
        
        # 尝试获取账户资金信息
        try:
            account_info = trader.query_stock_asset(acc)
            if account_info:
                print(f"获取到账户信息: {account_info}")
                # 检查account_info对象的属性并安全访问
                balance = getattr(account_info, 'balance', 0.0)
                if hasattr(account_info, 'm_dBalance'):
                    balance = account_info.m_dBalance
                
                available = getattr(account_info, 'available', 0.0)
                if hasattr(account_info, 'm_dAvailable'):
                    available = account_info.m_dAvailable
                
                cash = getattr(account_info, 'cash', 0.0)
                if hasattr(account_info, 'm_dCash'):
                    cash = account_info.m_dCash
                
                result = {
                    "success": True,
                    "message": "连接测试成功",
                    "account": account,
                    "path": path,
                    "balance": balance,
                    "available": available,
                    "cash": cash
                }
            else:
                result = {
                    "success": False,
                    "message": f"账户 {account} 不存在或未登录",
                    "account": account,
                    "path": path
                }
        except Exception as e:
            result = {
                "success": False,
                "message": f"测试账户连接失败: {str(e)}",
                "account": account,
                "path": path,
                "error_type": str(type(e).__name__)
            }
        
        # 停止交易线程
        trader.stop()
        print("交易线程已停止")
        
        return result
    
    except Exception as e:
        print(f"测试账户连接出错: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"测试账户连接出错: {str(e)}",
            "account": account,
            "path": r'C:\Program Files\821\迅投极速交易终端睿智融科版\userdata',
            "error_type": str(type(e).__name__)
        } 