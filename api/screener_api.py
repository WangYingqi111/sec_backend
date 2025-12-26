from fastapi import APIRouter, HTTPException
from schemas.screener_schema import ScreenerRequest, ScreenerResponse
from services.screener_svc import ScreenerService

from sec_core.log_config import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/list", response_model=ScreenerResponse)
async def get_screener_list(request: ScreenerRequest):
    """
    API 接口：根据条件筛选股票
    """
    logger.info(f"Receiving screener request: {request.dict()}")
    try:
        # 调用业务层
        stocks = ScreenerService.filter_stocks(
            start_date=request.start_date,
            industry_names=request.industry_name or [],
            min_periods=request.min_consecutive_periods,
            rev_rate=request.revenue_growth_rate,
            profit_rate=request.profit_growth_rate,
            condition=request.condition,
            period_type=request.period_type
        )
        
        return {
            "stocks": stocks,
            "count": len(stocks)
        }
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

### why use pass to omit the implementation?
@router.get("/chart/{sec_code}")
async def get_stock_chart(sec_code: str, period_type: str = "season"):
    # 调用 Service 获取图表数据
    # return ScreenerService.get_stock_chart_data(...)
    pass