from typing import List, Dict
from ..registry import tool_registry
import xtquant.xtdata as xtdata

'''
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
'''


### todo
