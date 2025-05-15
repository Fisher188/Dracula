from typing import List, Dict, Optional, Literal
from ..registry import tool_registry
import xtquant.xtdata as xtdata


@tool_registry.register(
    name="get_supported_data_types",
    description="获取QMT支持的所有数据类型",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def get_supported_data_types() -> Dict:
    """
    获取QMT支持的所有数据类型
    
    Returns:
        包含所有支持的数据类型的字典，每个数据类型包含name和desc两个字段
        
    样例数据：
    >>> xtdata.get_period_list()
    [
        {'name': 'tick', 'desc': '分笔'},
        {'name': '1m', 'desc': 'K线 1分钟'},
        {'name': '5m', 'desc': 'K线 5分钟'},
        ...
    ]
    """
    return xtdata.get_period_list()


@tool_registry.register(
    name="get_markets",
    description="获取QMT支持的所有交易市场",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def get_markets() -> Dict:
    """
    获取QMT支持的所有交易市场
    
    Returns:
        包含所有支持的交易市场的字典，key为市场代码，value为市场名称
        
    样例数据：
    >>> xtdata.get_markets()
    {
        'SH': '上交所',
        'SZ': '深交所', 
        'BJ': '北交所',
        'HK': '港交所',
        'HGT': '沪港通',
        'SGT': '深港通',
        'IF': '中金所',
        'SF': '上期所',
        'DF': '大商所',
        'ZF': '郑商所',
        'GF': '广期所',
        'INE': '能源交易所',
        'SHO': '上证期权',
        'SZO': '深证期权',
        'BKZS': '板块指数'
    }
    """
    return xtdata.get_markets()


@tool_registry.register(
    name="get_trading_dates",
    description="获取指定市场的交易日列表",
    input_schema={
        "type": "object",
        "required": ["market"],
        "properties": {
            "market": {
                "type": "string",
                "description": "市场代码，如'SH'代表上交所"
            }
        }
    }
)
async def get_trading_dates(market: str) -> List:
    """
    获取指定市场的交易日列表
    
    Args:
        market: 市场代码，如'SH'代表上交所
    
    Returns:
        交易日列表，每个元素为Unix时间戳(毫秒)
        
    样例数据：
    >>> xtdata.get_trading_dates('SH')[::500]
    [661536000000, 723657600000, 785520000000, 848937600000, 913305600000, 
     979142400000, 1046016000000, 1111075200000, 1176134400000, 1240848000000, 
     1305734400000, 1371139200000, 1435680000000, 1500393600000, 1565020800000, 
     1629820800000, 1694707200000]
    """
    return xtdata.get_trading_dates(market)


@tool_registry.register(
    name="get_market_contracts",
    description="获取指定市场的合约列表",
    input_schema={
        "type": "object",
        "required": ["market"],
        "properties": {
            "market": {
                "type": "string", 
                "description": "市场代码，如'SH'代表上交所"
            }
        }
    }
)
async def get_market_contracts(market: str) -> List[str]:
    """
    获取指定市场的合约列表
    
    Args:
        market: 市场代码，如'SH'代表上交所
    
    Returns:
        合约代码列表
        
    样例数据:
    >>> xtdata.get_stock_list_in_sector('SH')[::100]
    ['000001.SH', '000114.SH', '000932.SH', '019595.SH', '019755.SH', '113024.SH',
     '113671.SH', '115520.SH', '118025.SH', '127784.SH', '127926.SH', '136705.SH']
    """
    return xtdata.get_stock_list_in_sector(market)


@tool_registry.register(
    name="get_instrument_detail",
    description="获取合约的基本信息",
    input_schema={
        "type": "object",
        "required": ["instrument_code"],
        "properties": {
            "instrument_code": {
                "type": "string", 
                "description": "合约代码，如'002594.SZ'"
            }
        }
    }
)
async def get_instrument_detail(instrument_code: str) -> Dict:
    """
    获取合约的基本信息
    
    Args:
        instrument_code: 合约代码，如'002594.SZ'
    
    Returns:
        包含合约基本信息的字典，包括:
        - ExchangeID (string): 合约市场代码
        - InstrumentID (string): 合约代码
        - InstrumentName (string): 合约名称
        - ProductID (string): 合约的品种ID(期货)
        - ProductName (string): 合约的品种名称(期货)
        - ExchangeCode (string): 交易所代码
        - UniCode (string): 统一规则代码
        - CreateDate (str): 上市日期(期货)
        - OpenDate (str): IPO日期(股票)
        - ExpireDate (int): 退市日或者到期日
        - PreClose (float): 前收盘价格
        - SettlementPrice (float): 前结算价格
        - UpStopPrice (float): 当日涨停价
        - DownStopPrice (float): 当日跌停价
        - FloatVolume (float): 流通股本
        - TotalVolume (float): 总股本
        - LongMarginRatio (float): 多头保证金率
        - ShortMarginRatio (float): 空头保证金率
        - PriceTick (float): 最小价格变动单位
        - VolumeMultiple (int): 合约乘数(对期货以外的品种，默认是1)
        - MainContract (int): 主力合约标记，1、2、3分别表示第一主力合约，第二主力合约，第三主力合约
        - LastVolume (int): 昨日持仓量
        - InstrumentStatus (int): 合约停牌状态
        - IsTrading (bool): 合约是否可交易
        - IsRecent (bool): 是否是近月合约
        - OpenInterestMultiple (int): 交割月持仓倍数
        
    样例数据：
    >>> xtdata.get_instrument_detail('002594.SZ')
    {'ExchangeID': 'SZ', 'InstrumentID': '002594', 'InstrumentName': '比亚迪',
     'OpenDate': '20110630', 'ExpireDate': '99999999', 'PreClose': 382.5,
     'UpStopPrice': 420.75, 'DownStopPrice': 344.25, 'FloatVolume': 1162413941.0,
     'TotalVolume': 3039065855.0, 'PriceTick': 0.01}
    """
    return xtdata.get_instrument_detail(instrument_code)


@tool_registry.register(
    name="get_full_tick",
    description="获取股票最新的盘口、价格、成交量等实时行情数据",
    input_schema={
        "type": "object",
        "required": ["stock_codes"],
        "properties": {
            "stock_codes": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "股票代码列表，如：['600000.SH']"
            }
        }
    }
)
async def get_full_tick(stock_codes: List[str]) -> Dict:
    """
    获取股票最新的盘口、价格、成交量等实时行情数据
    
    Args:
        stock_codes: 股票代码列表，如：['600000.SH']
    
    Returns:
        包含股票实时行情数据的字典，包括:
        - 最新价格(lastPrice)
        - 开盘价(open)、最高价(high)、最低价(low)
        - 昨收价(lastClose)
        - 成交额(amount)、成交量(volume)
        - 五档盘口价格(askPrice/bidPrice)和量(askVol/bidVol)
        等信息
        
    样例数据：
    >>> xtdata.get_full_tick(['600000.SH'])
    {'600000.SH': {'time': 1743403935000, 'timetag': '20250331 14:52:15', 'lastPrice': 10.44,
        'open': 10.47, 'high': 10.63, 'low': 10.35, 'lastClose': 10.44, 'amount': 493393500,
        'volume': 469673, 'pvolume': 46967317, 'tickvol': 186, 'stockStatus': 3, 'openInt': 13,
        'transactionNum': 56594, 'settlementPrice': 0, 'lastSettlementPrice': 0, 'pe': 0,
        'askPrice': [10.44, 0, 0, 0, 0], 'bidPrice': [10.43, 0, 0, 0, 0],
        'askVol': [846, 0, 0, 0, 0], 'bidVol': [5995, 0, 0, 0, 0]}}
    """
    return xtdata.get_full_tick(stock_codes) 


@tool_registry.register(
    name="download_history_data",
    description="补充历史行情数据",
    input_schema={
        "type": "object",
        "required": ["stock_code", "period"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "合约代码，如：'002594.SZ'"
            },
            "period": {
                "type": "string", 
                "description": "周期"
            },
            "start_time": {
                "type": "string",
                "description": "起始时间",
                "default": ""
            },
            "end_time": {
                "type": "string",
                "description": "结束时间",
                "default": ""
            },
            "incrementally": {
                "type": ["boolean", "null"],
                "description": "是否增量下载,None时使用start_time控制,start_time为空则增量下载",
                "default": None
            }
        }
    }
)
async def download_history_data(stock_code: str, period: str, start_time: str = "", end_time: str = "", incrementally: Optional[bool] = None) -> Dict:
    """
    补充历史行情数据
    
    Args:
        stock_code: 合约代码，如：'002594.SZ'
        period: 周期
        start_time: 起始时间，默认为空字符串
        end_time: 结束时间，默认为空字符串
        incrementally: 是否增量下载
            - bool: 是否增量下载
            - None: 使用start_time控制，start_time为空则增量下载
    
    Returns:
        包含下载结果的字典，包括:
        - start_time: 开始时间
        - end_time: 结束时间  
        - count: 数据条数
        
    样例数据：
    >>> xtdata.download_history_data('002594.SZ', '1d', '', '', True)
    {'002594.SZ': {'start_time': datetime.datetime(2011, 6, 30, 0, 0), 
                   'end_time': datetime.datetime(2025, 3, 31, 0, 0), 
                   'count': 3328}}
    """
    return xtdata.download_history_data(stock_code, period, start_time, end_time, incrementally)


@tool_registry.register(
    name="get_kline",
    description="获取单个股票的K线数据",
    input_schema={
        "type": "object",
        "required": ["field_list", "stock_code"],
        "properties": {
            "field_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "数据字段列表，如['close', 'volume']"
            },
            "stock_code": {
                "type": "string",
                "description": "合约代码，如'002594.SZ'"
            },
            "period": {
                "type": "string",
                "description": "K线周期，支持1m,3m,5m,10m,15m,30m,60m,120m,180m,240m,1h,2h,3h,4h,1d,2d,3d,5d,1w,1mon,1q,1hy,1y",
                "default": "1d"
            },
            "start_time": {
                "type": "string",
                "description": "起始时间",
                "default": ""
            },
            "end_time": {
                "type": "string",
                "description": "结束时间",
                "default": ""
            },
            "count": {
                "type": "integer",
                "description": "数据个数，-1表示全部数据",
                "default": -1
            },
            "dividend_type": {
                "type": "string",
                "description": "除权方式",
                "default": "none"
            },
            "fill_data": {
                "type": "boolean",
                "description": "是否向后填充空缺数据",
                "default": True
            }
        }
    }
)
async def get_kline(
    field_list: List[str],
    stock_code: str,
    period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = -1,
    dividend_type: str = "none",
    fill_data: bool = True
) -> Dict:
    """
    获取单个股票的K线数据
    
    Args:
        field_list: 数据字段列表，传空则为全部字段。可用字段包括:
            - time: 时间戳
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - amount: 成交额
            - settelementPrice: 今结算
            - openInterest: 持仓量
            - preClose: 前收价
            - suspendFlag: 停牌标记(0-正常 1-停牌 -1-当日起复牌)
        stock_code: 合约代码，如：'002594.SZ'
        period: K线周期，默认为'1d'。支持:
            - 分钟: 1m, 3m, 5m, 10m, 15m, 30m, 60m, 120m, 180m, 240m
            - 小时: 1h, 2h, 3h, 4h
            - 日: 1d, 2d, 3d, 5d
            - 周: 1w
            - 月: 1mon
            - 季: 1q
            - 半年: 1hy
            - 年: 1y
        start_time: 起始时间，默认为空字符串
        end_time: 结束时间，默认为空字符串
        count: 数据个数，默认为-1
            - count >= 0: 若指定了start_time和end_time，以end_time为基准向前取count条
            - count >= 0: 若start_time和end_time缺省，取本地数据最新的count条数据
            - count < 0: 若start_time、end_time、count都缺省，取本地全部数据
        dividend_type: 除权方式，默认为'none'
        fill_data: 是否向后填充空缺数据，默认为True
    
    Returns:
        返回dict { stock_code: { field1: [values], field2: [values], ... } }
        - field1, field2等为数据字段
        - values为对应字段的数据列表
        - time字段为Unix时间戳(毫秒)
        - stime字段为格式化的时间字符串
            
    Note:
        - 时间范围为闭区间
        - 这个接口专用于获取单个股票的K线数据
        
    样例数据:
    >>> xtdata.get_market_data_ex_ori(field_list=['close', 'volume'], 
                                    stock_list=['002594.SZ'], 
                                    period='1d')
    {'002594.SZ': {
        'time': [1743350400000], 
        'stime': ['20250331'],
        'close': [374.9], 
        'volume': [115784]
    }}
    """
    return xtdata.get_market_data_ex_ori(
        field_list=field_list,
        stock_list=[stock_code],
        period=period,
        start_time=start_time,
        end_time=end_time,
        count=count,
        dividend_type=dividend_type,
        fill_data=fill_data
    )


@tool_registry.register(
    name="download_financial_data",
    description="下载单个股票的财务数据",
    input_schema={
        "type": "object",
        "required": ["stock_code"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "合约代码，如'002594.SZ'"
            }
        }
    }
)
async def download_financial_data(stock_code: str) -> None:
    """
    下载单个股票的财务数据
    
    Args:
        stock_code: 合约代码，如'002594.SZ'
    
    Returns:
        None
        
    Note:
        同步执行，补充数据完成后返回
    """
    return xtdata.download_financial_data([stock_code])


@tool_registry.register(
    name="get_financial_data",
    description="获取单个股票的财务数据",
    input_schema={
        "type": "object",
        "required": ["stock_code"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "合约代码，如'002594.SZ'"
            },
            "table_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "财务数据表名称列表，如['Balance', 'Income']",
                "default": []
            }
        }
    }
)
async def get_financial_data(stock_code: str, table_list: List[str] = []) -> Dict:
    """
    获取单个股票的财务数据
    
    Args:
        stock_code: 合约代码，如'002594.SZ'
        table_list: 财务数据表名称列表，可选值:
            - Balance: 资产负债表
            - Income: 利润表  
            - CashFlow: 现金流量表
            - Capital: 股本表
            - Holdernum: 股东数
            - Top10holder: 十大股东
            - Top10flowholder: 十大流通股东
            - Pershareindex: 每股指标
    
    Returns:
        包含财务数据的字典，格式为:
        {stock_code: {table_name: data_dict}}
        其中data_dict为将DataFrame转换成的字典
        
    样例数据：
    >>> xtdata.get_financial_data(['002594.SZ'], ['Balance'])
    {'002594.SZ': {'Balance': {'total_assets': [1000000, 2000000], 'total_liabilities': [500000, 1000000]}}}
    """
    result = xtdata.get_financial_data([stock_code], table_list)
    
    # 将每个DataFrame转换为字典
    for stock in result:
        for table in result[stock]:
            if hasattr(result[stock][table], 'to_dict'):
                result[stock][table] = result[stock][table].to_dict('list')
    
    return result





