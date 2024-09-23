import akshare as ak
import pandas as pd
from datetime import date
import time
import random

# 获取今天的日期
today = date.today().strftime("%Y%m%d")

# 获取 A 股股票列表
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()

# 筛选条件：剔除科创板（代码以 688 开头）、北交所（代码以 8 或 43 开头）以及名称中带有'ST'的股票
filtered_stocks = stock_zh_a_spot_em_df[
    ~stock_zh_a_spot_em_df['代码'].str.startswith('688') &
    ~stock_zh_a_spot_em_df['代码'].str.startswith('689') &
    ~stock_zh_a_spot_em_df['代码'].str.startswith('8') &
    ~stock_zh_a_spot_em_df['代码'].str.startswith('43') &
    ~stock_zh_a_spot_em_df['名称'].str.contains('ST')
].copy()  # 创建副本

# 只保留股票代码、股票名称和当前股价（最新价）三列
result_df = filtered_stocks[['代码', '名称', '最新价','市盈率-动态','市净率','总市值']]

# 使用 stock_lrb_em 接口查询今天的所有股票利润表
profit_df = ak.stock_lrb_em(date="20240630")

# 筛选出与 filtered_stocks.csv 中股票代码匹配的数据
matched_profit_df = profit_df[profit_df['股票代码'].isin(result_df['代码'])]

# 合并匹配后的利润数据到 result_df
result_df = pd.merge(result_df, matched_profit_df[['股票代码', '营业利润']], left_on='代码', right_on='股票代码', how='left')

# 合并后，可以删除多余的 '股票代码' 列
result_df.drop('股票代码', axis=1, inplace=True)

# 删除'营业利润'为负数的股票
result_df = result_df[result_df['营业利润'] >= 1000000]

# 删除当前股票价格>100 元的股票
result_df = result_df[result_df['最新价'] <= 100]

# 删除'市盈率-动态'>100 的股票
result_df = result_df[result_df['市盈率-动态'] <= 80]

# 删除'市净率'>50 的股票
result_df = result_df[result_df['市净率'] <= 20]

# 在第一列新增编号列
result_df.insert(0, '编号', range(1, len(result_df) + 1))

# 新增'代码_spot'列
result_df.insert(1, '代码_spot', result_df['代码'].apply(lambda x: 'sh'+x if x.startswith('6') else 'sz'+x))

# 将总市值单位由元换算为亿元
result_df['总市值'] = result_df['总市值'] / 100000000

# 将营业利润单位由元换算为万元
result_df['营业利润'] = result_df['营业利润'] / 10000

# 将结果保存为 CSV 文件，覆盖原文件
result_df.to_csv(r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\filtered_stocks.csv', index=False)