from typing import List
from ..registry import tool_registry
import xtquant.xtdata as xtdata


@tool_registry.register(
    name="get_sector_list",
    description="获取所有可用的板块列表，支持可选的关键字过滤",
    input_schema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "关键字列表,当任意关键字存在于板块名称中时返回该板块"
            }
        }
    }
)
async def get_sector_list(keywords: List[str] = None) -> List[str]:
    """
    获取所有可用的板块列表
    
    Args:
        keywords: 关键字列表,当任意关键字存在于板块名称中时返回该板块。如果为None则返回所有板块。
    
    Returns:
        板块名称列表
        
    样例数据:
    >>> xtdata.get_sector_list()[::200]
    ['沪深A股', '上证A股', '深证A股', '创业板', '科创板', '沪深300', '上证50',
     '000809', '380稳定', 'CSWD生科等权', 'DY2河南省南阳市', 'GICS3建筑材料[us]',
     'GICS4餐馆[us]', 'GN举牌', 'GN动漫', 'GN大金融', 'GN数据要素', 'GN河南国企改革',
     'GN疫情监测', 'GN节能减排', 'GN阅兵', 'HKSW2工业工程', 'HKSW3教育',
     'HKTGN中资券 商股[HK]', 'HKTGN金融IC[HK]', 'SW2化学纤维', 'SW2装修装饰',
     'SW3其他橡胶制品', 'SW3安防设备', 'SW3炼油化工', 'SW3营销服 务', 'TGNDRGDIP',
     'TGN新材料概念', 'TGN黑龙江自贸区', 'THY3农商行', 'THY3锂电池', 'USTGN酒店[us]',
     '中小等权', '其他传媒', '国证保证', '成份Ｂ指', '消费服务', '物流Ⅲ',
     '计算机(SW港股通)']
    
    >>> get_sector_list(['金融', 'GN'])
    ['GN大金融', 'GN金融科技', 'HKTGN金融IC[HK]', 'GN举牌', 'GN动漫', 'GN数据要素']
    """
    sectors = xtdata.get_sector_list()
    if keywords is None:
        return sectors
        
    result = []
    for sector in sectors:
        if any(keyword in sector for keyword in keywords):
            result.append(sector)
    return result


@tool_registry.register(
    name="get_sector_constituents", 
    description="获取指定板块的成分股列表",
    input_schema={
        "type": "object",
        "required": ["sector"],
        "properties": {
            "sector": {
                "type": "string",
                "description": "板块名称，如'沪深300'"
            }
        }
    }
)
async def get_sector_constituents(sector: str) -> List[tuple[str, str]]:
    """
    获取指定板块的成分股列表
    
    Args:
        sector: 板块名称，如'沪深300'
    
    Returns:
        成分股代码和名称的元组列表
        
    样例数据:
    [('000001.SZ', '平安银行'), ('000002.SZ', '万 科Ａ'), ('000063.SZ', '中兴通讯'), ('000100.SZ', 'TCL科技')]
    """
    sl = xtdata.get_stock_list_in_sector(sector)
    result = []
    unknown_instruments = []
    for s in sl:
        instrument = xtdata.get_instrument_detail(s)
        if instrument is not None:
            result.append((s, instrument['InstrumentName']))
        else:
            result.append((s, '未知品种'))
            unknown_instruments.append(s)
    
    if unknown_instruments:
        print(f"发现未知品种: {', '.join(unknown_instruments)}")
        print("提示: 可尝试调用 download_history_contracts() 更新过期合约数据")
    return result


@tool_registry.register(
    name="download_sector_data",
    description="下载板块数据（在每个交易日早上9点更新一次即可，耗时几十秒较长，可推荐用户在界面手工下载更新）",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def download_sector_data() -> None:
    """
    下载板块数据（在每个交易日早上9点更新一次即可，耗时几十秒较长，可推荐用户在界面手工下载更新）
    
    Returns:
        无返回
        
    样例数据:
    >>> xtdata.download_sector_data()
    """
    print("下载板块数据（在每个交易日早上9点更新一次即可，耗时几十秒较长，可推荐用户在界面手工下载更新）")
    xtdata.download_sector_data()
    print("下载板块数据完成")


@tool_registry.register(
    name="download_history_contracts",
    description="下载过期合约数据（每个交易日早9点更新一次即可，如果发现无效品种可能是合约过期，可以尝试更新这个过期合约数据）",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def download_history_contracts() -> None:
    """
    下载过期合约数据（每个交易日早9点更新一次即可，如果发现无效品种可能是合约过期，可以尝试更新这个过期合约数据）
    
    Returns:
        无返回
        
    样例数据:
    >>> xtdata.download_history_contracts()
    """
    print("开始下载过期合约数据（耗时较长约几十秒）...")
    xtdata.download_history_contracts()
    print("下载过期合约数据完成")


# 全局缓存字典,存储股票到板块的映射关系
_stock_sector_cache = {}
_stock_sector_cache_initialized = False

def _build_stock_sector_cache():
    """构建股票到板块的缓存映射"""
    global _stock_sector_cache, _stock_sector_cache_initialized
    if not _stock_sector_cache_initialized:
        print("正在建立股票板块缓存，请稍等...")
        # 获取所有板块
        all_sectors = xtdata.get_sector_list()
        # 遍历每个板块,获取成分股并建立反向索引
        for sector in all_sectors:
            stocks = xtdata.get_stock_list_in_sector(sector)
            for stock in stocks:
                if stock not in _stock_sector_cache:
                    _stock_sector_cache[stock] = []
                _stock_sector_cache[stock].append(sector)
        _stock_sector_cache_initialized = True

@tool_registry.register(
    name="get_stock_sectors", 
    description="获取股票所属的所有板块",
    input_schema={
        "type": "object",
        "required": ["stock_code"],
        "properties": {
            "stock_code": {
                "type": "string",
                "description": "股票代码，如'002594.SZ'"
            }
        }
    }
)
async def get_stock_sectors(stock_code: str) -> List[str]:
    """
    获取股票所属的所有板块
    
    Args:
        stock_code: 股票代码，如'002594.SZ'
        
    Returns:
        板块代码列表
        
    样例数据:
    >>> xtdata.get_stock_sectors('002594.SZ')
    ['801880.SH', '801880.SI', '850111.SI', '850111.SH', '801010.SI', '801010.SH']
    """
    # 确保缓存已建立
    _build_stock_sector_cache()
    # 从缓存中获取结果
    return _stock_sector_cache.get(stock_code, [])


# 合约名称到代码的缓存映射
_stock_name_cache = {}

def _build_stock_name_cache_for_market(market: str):
    """为指定市场构建合约名称到代码的缓存映射"""
    global _stock_name_cache
    # 检查是否已经缓存了该市场的数据
    market_cached = any(k.startswith(f"{market}:") for k in _stock_name_cache)
    if market_cached:
        return

    print(f"正在建立{market}市场的合约名称缓存，请稍等...")
    stocks = xtdata.get_stock_list_in_sector(market)
    for stock in stocks:
        # 获取合约详情信息
        detail = xtdata.get_instrument_detail(stock)
        if detail and 'InstrumentName' in detail:
            name = detail['InstrumentName']
            _stock_name_cache[f"{market}:{name}"] = stock

@tool_registry.register(
    name="get_stock_code_by_name",
    description="根据合约名称获取合约代码，可传入推定存在于的市场的列表",
    input_schema={
        "type": "object", 
        "required": ["stock_name"],
        "properties": {
            "stock_name": {
                "type": "string",
                "description": "合约名称，如'比亚迪'"
            },
            "markets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要搜索的市场列表，按优先级排序。如果为None，则按默认顺序搜索所有市场。例如['SZ', 'SH']表示只在深交所和上交所中搜索。",
                "default": ["SZ", "SH", "BJ"]
            }
        }
    }
)
async def get_stock_code_by_name(stock_name: str, markets: List[str] = None) -> str:
    """
    根据合约名称获取合约代码
    
    Args:
        stock_name: 合约名称，如'比亚迪'
        markets: 要搜索的市场列表，按优先级排序。如果为None，则按默认顺序搜索。
        
    Returns:
        合约代码，如'002594.SZ'。如果未找到则返回空字符串
        
    样例数据:
    >>> get_stock_code_by_name('比亚迪')
    '002594.SZ'
    """
    if markets is None:
        all_markets = [
            'SH', 'SZ', 'BJ'
            , 'BKZS'
            , 'IF', 'SF', 'DF', 'ZF', 'GF', 'INE'
            , 'SHO', 'SZO'
            , 'HK', 'HGT', 'SGT'
        ]
        available_markets = set(xtdata.get_markets().keys())
        markets = [m for m in all_markets if m in available_markets]
        remaining = [m for m in available_markets if m not in all_markets]
        markets.extend(remaining)
        
    # 按优先级尝试各个市场
    for market in markets:
        _build_stock_name_cache_for_market(market)
        cache_key = f"{market}:{stock_name}"
        if cache_key in _stock_name_cache:
            return _stock_name_cache[cache_key]
            
    raise ValueError(f"未找到名称为'{stock_name}'的合约")

