import pandas as pd
import random

# 读取原始 CSV 文件
file_path = r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\filtered_stocks.csv'
df = pd.read_csv(file_path, dtype={'代码': str})  # 明确指定代码列为字符串类型

# 筛选出 60 开头、30 开头、00 开头的股票数据
df_60 = df[df['代码_spot'].str.startswith('sh60')]
df_30 = df[df['代码_spot'].str.startswith('sz30')]
df_00 = df[df['代码_spot'].str.startswith('sz00')]

# 随机抽取各 30 支股票，如果数据量不足则抽取全部
def random_sample(df_sub):
    n = min(30, len(df_sub))
    return random.sample(list(df_sub.index), n)

random_60 = random_sample(df_60)
random_30 = random_sample(df_30)
random_00 = random_sample(df_00)

selected_df = pd.concat([df.iloc[random_60], df.iloc[random_30], df.iloc[random_00]])

# 删除原有的编号列
if '编号' in selected_df.columns:
    del selected_df['编号']

# 新增从 1 开始递增的编号列
selected_df.insert(0, '编号', range(1, len(selected_df)+1))

# 将筛选出的数据保存为新的 CSV 文件
output_path = r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\StockPoolRandom.csv'
selected_df.to_csv(output_path, index=False)