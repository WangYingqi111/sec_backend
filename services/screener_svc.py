import pandas as pd
from sec_core.db_man import LICO_FN_Helper  # 导入共享模块
from sec_core.log_config import setup_logger

logger = setup_logger(__name__)

class ScreenerService:
    
    @staticmethod
    def filter_stocks(
        start_date: str,
        industry_names: list,
        min_periods: int,
        rev_rate: float,
        profit_rate: float,
        condition: str,
        period_type: str
    ) -> list:
        """
        核心筛选逻辑：获取数据 -> 分组 -> 计算连续增长 -> 返回代码列表
        """
        try:

            logger.info(
                "filter_stocks params: start_date=%s, industry_names=%s, period_type=%s", start_date, industry_names, period_type)

            # 1. 映射周期类型到数据库字段值
            datemdd_filter = "年报" if period_type == "year" else "季报"
            
            # 2. 从数据库获取原始数据 (调用 db_man)
            # 注意：此处假设 get_performance_data 能够处理 industry_codes 参数传入 industry_names
            # 如果 db_man 里的 industry_codes 需要编码，这里可能需要转换，暂时假设直接传名称
            df_raw = LICO_FN_Helper.get_performance_data(
                period_type=1,
                from_date=start_date,
                industry_codes=industry_names 
            )
            
            if df_raw.empty:
                return []

            # 3. 初步过滤：只取对应的报表类型
            df = df_raw.copy()

            # 4. 确定使用的列名 (年报用同比 YSTZ/SJLTZ，季报用环比 YSHZ/SJLHZ)
            # 也可以根据您的具体业务逻辑调整，比如季报也看同比
            rev_col = 'YSTZ' if period_type == "year" else 'YSHZ'
            profit_col = 'SJLTZ' if period_type == "year" else 'SJLHZ'

            # 5. 定义分组筛选函数
            def check_consecutive(group):
                # 必须按时间倒序排列 (最近的在前面)
                group = group.sort_values(by='REPORTDATE', ascending=False)
                
                # 如果数据行数少于要求的连续期数，直接淘汰
                if len(group) < min_periods:
                    return False

                # 取最近的 N 期
                recent_n = group.iloc[:min_periods]
                
                # 检查阈值 (注意处理 None/NaN 情况，通常填 0 或 -999)
                rev_vals = recent_n[rev_col].fillna(-999)
                profit_vals = recent_n[profit_col].fillna(-999)

                rev_check = rev_vals >= (rev_rate * 100) # 假设数据库存的是百分数(如20.5)，输入是小数(0.2)
                profit_check = profit_vals >= (profit_rate * 100)

                if condition == "AND":
                    # 所有 N 期都必须满足 且 (营收 和 利润)
                    return (rev_check & profit_check).all()
                else:
                    # 所有 N 期都必须满足 (营收 或 利润)
                    return (rev_check | profit_check).all()

            # 6. 执行筛选
            # group_keys=True 保持索引，filter 返回的是符合条件的原始行
            qualified_df = df.groupby('SECURITY_CODE').filter(check_consecutive)
            
            # 7. 提取结果 (去重)
            unique_secs = qualified_df.drop_duplicates(subset=['SECURITY_CODE'])
            
            result_list = []
            for _, row in unique_secs.iterrows():
                result_list.append({
                    "security_code": row['SECURITY_CODE'],
                    "security_name": row.get('SECURITY_NAME_ABBR', 'N/A'),
                    "industry": row.get('PUBLISHNAME', 'N/A')
                })
                
            return result_list

        except Exception as e:
            logger.error(f"Error in ScreenerService: {e}")
            raise e # 抛出异常给 API 层处理

    @staticmethod
    def get_stock_chart_data(sec_code: str, period_type: str, limit: int = 8):
        df = LICO_FN_Helper.get_performance_data(
            period_type=1 if period_type == "season" else 2,
            sec_codes=[sec_code]
        )

        if df.empty:
            return []

        df = df.sort_values("REPORTDATE").tail(limit)

        return {
            "dates": df["REPORTDATE"].dt.strftime("%Y-%m-%d").tolist(),
            "revenue": df["TOTAL_OPERATE_INCOME"].tolist(),
            "profit": df["PARENT_NETPROFIT"].tolist()
        }
