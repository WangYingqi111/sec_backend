from pydantic import BaseModel, Field
from typing import List, Optional

# 请求模型：前端发来的筛选条件
class ScreenerRequest(BaseModel):
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    industry_name: Optional[List[str]] = Field(None, description="行业名称列表")
    min_consecutive_periods: int = Field(..., ge=1, description="最小连续期数")
    revenue_growth_rate: float = Field(..., description="营收增长率阈值 (如 0.2 代表 20%)")
    profit_growth_rate: float = Field(..., description="利润增长率阈值")
    condition: str = Field(..., pattern="^(AND|OR)$", description="条件连接符")
    period_type: str = Field(..., pattern="^(year|season)$", description="周期: year 或 season")

# 响应模型：单个股票的简要信息
class StockItem(BaseModel):
    security_code: str
    security_name: str
    industry: str

# 响应模型：股票列表
class ScreenerResponse(BaseModel):
    stocks: List[StockItem]
    count: int