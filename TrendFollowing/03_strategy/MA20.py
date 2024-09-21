import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import math
import datetime

# 回测数据输入
backtest_stock_code = "300793"
backtest_start_date = "20220101"
backtest_start_date_timestamp ='2022 - 01 - 01'
backtest_end_date = '20240921'
backtest_end_date_timestamp ='2024 - 09 - 21'

warnings.filterwarnings("ignore", category=UserWarning)
import matplotlib as mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol= backtest_stock_code, period="daily", start_date=backtest_start_date, end_date=backtest_end_date,
                                         adjust="hfq")

print(stock_zh_a_hist_df)
# 检查列名
if '收盘' not in stock_zh_a_hist_df.columns:
    print(stock_zh_a_hist_df.columns)
    raise ValueError("数据中没有 '收盘' 列，请检查数据格式")

# 计算20日均线
stock_zh_a_hist_df['MA20'] = stock_zh_a_hist_df['收盘'].rolling(window=20).mean()

# 初始资金
initial_money = 100000
# 股票数量
stock_num = 0
# 交易记录
trade_records = []
# 记录每日总资产
daily_total_assets = []
# 记录每日收益率
daily_income_rates = []
# 标记是否可卖，买入后第一天不可卖
can_sell = True
# 记录买入日期
buy_date = None
# 记录买入成本价
buy_cost_price = 0
# 记录最近一次买入价格
last_buy_price = 0

for i in range(2, len(stock_zh_a_hist_df)):
    # 优化后的买入策略
    if stock_num == 0 and stock_zh_a_hist_df['收盘'].iloc[i - 2] <= stock_zh_a_hist_df['MA20'].iloc[i - 2] and \
            stock_zh_a_hist_df['收盘'].iloc[i - 1] > stock_zh_a_hist_df['MA20'].iloc[i - 1] and \
            stock_zh_a_hist_df['成交量'].iloc[i - 1] > 1.1 * stock_zh_a_hist_df['成交量'].iloc[i - 2]:
        # 买入
        buy_price = stock_zh_a_hist_df['开盘'].iloc[i]
        can_buy_num = initial_money // buy_price
        # 每次最少买100股
        real_buy_num = (can_buy_num // 100) * 100
        if real_buy_num < 100:
            real_buy_num = 0
        # 当real_buy_num为0时，不进行买入操作，不记录买入信息
        if real_buy_num > 0:
            cost = real_buy_num * buy_price
            stock_num += real_buy_num
            initial_money -= cost
            buy_cost_price = cost / real_buy_num if real_buy_num else 0
            last_buy_price = buy_price
            trade_records.append([stock_zh_a_hist_df['日期'].iloc[i], '买', real_buy_num, buy_price,
                                   initial_money + stock_num * stock_zh_a_hist_df['收盘'].iloc[i],
                                   stock_num * stock_zh_a_hist_df['收盘'].iloc[i], initial_money])
            buy_date = stock_zh_a_hist_df['日期'].iloc[i]
            can_sell = False

    # 根据日期判断是否可以将can_sell置为True
    if buy_date and stock_zh_a_hist_df['日期'].iloc[i]!= buy_date:
        can_sell = True

    # 优化后的卖出策略
    if stock_num > 0 and can_sell:
        if stock_zh_a_hist_df['收盘'].iloc[i - 1] > stock_zh_a_hist_df['MA20'].iloc[i - 1] and \
                stock_zh_a_hist_df['收盘'].iloc[i] < stock_zh_a_hist_df['MA20'].iloc[i]:
            # / stock_zh_a_hist_df['最低'].iloc[i] < stock_zh_a_hist_df['MA20'].iloc[i]
            sell_price = stock_zh_a_hist_df['开盘'].iloc[i]
            get_money = stock_num * sell_price

            buy_total_value = last_buy_price * stock_num
            sell_total_value = stock_num * sell_price
            sell_income_rate = (sell_total_value - buy_total_value) / buy_total_value * 100

            stock_num = 0
            initial_money += get_money
            can_sell = True

            trade_records.append([stock_zh_a_hist_df['日期'].iloc[i], '卖', stock_num, sell_price, initial_money, 0,
                                   initial_money, sell_income_rate])
        else:
            # 检查是否存在满足亏损5%卖出条件的价格
            # price_to_sell = max(buy_cost_price * 0.95, stock_zh_a_hist_df['最低'].iloc[i])
            price_to_sell = buy_cost_price * 0.95
            if price_to_sell >= stock_zh_a_hist_df['最低'].iloc[i] and price_to_sell <= stock_zh_a_hist_df['最高'].iloc[i]:
                sell_price = price_to_sell
                get_money = stock_num * sell_price

                buy_total_value = last_buy_price * stock_num
                sell_total_value = stock_num * sell_price
                sell_income_rate = (sell_total_value - buy_total_value) / buy_total_value * 100

                stock_num = 0
                initial_money += get_money
                can_sell = True

                trade_records.append([stock_zh_a_hist_df['日期'].iloc[i], '卖', stock_num, sell_price, initial_money, 0,
                                       initial_money, sell_income_rate])

    # 计算总资产（包含股票市值和剩余资金）
    total_asset = stock_num * stock_zh_a_hist_df['收盘'].iloc[i] + initial_money
    daily_total_assets.append([stock_zh_a_hist_df['日期'].iloc[i], total_asset])
    income_rate = (total_asset - 100000) / 100000 * 100
    daily_income_rates.append([stock_zh_a_hist_df['日期'].iloc[i], income_rate])

# 打印交易信息
trade_times = len([record for record in trade_records if record[1] in ['买', '卖']]) // 2
win_count = 0
for record in trade_records:
    if len(record) == 7:
        print("日期：{}，操作：{}，数量：{}，成交价格：{}，总资产：{}，持有市值：{}，闲置资金：{}".format(record[0], record[1], record[2], record[3],
                                                                              round(record[4], 2), round(record[5], 2),
                                                                              round(record[6], 2)))
    else:
        if record[7] > 0:
            win_count += 1
        print("日期：{}，操作：{}，数量：{}，成交价格：{}，总资产：{}，持有市值：{}，闲置资金：{}，卖出收益率：{:.2f}%".format(
            record[0], record[1], record[2], record[3], round(record[4], 2), round(record[5], 2), round(record[6], 2),
            record[7]))

# 计算投资区间天数
start_date = pd.Timestamp(backtest_start_date_timestamp)
end_date = pd.Timestamp(backtest_end_date_timestamp)
investment_days = (end_date - start_date).days

# 计算策略投资收益、策略区间收益率、年化收益率、交易胜率
strategy_income = total_asset - 100000
strategy_income_rate = strategy_income / 100000 * 100
annualized_income_rate = (math.pow((total_asset / 100000), 365 / investment_days) - 1) * 100
win_rate = win_count / trade_times if trade_times > 0 else 0

# 获取回测结束后的总资产
end_total_asset = daily_total_assets[-1][1]

print("回测结束后总资产：{:.2f}，策略投资收益：{:.2f}，策略区间收益率：{:.2f}%，年化收益率：{:.2f}%，交易胜率：{:.2f}%，交易次数：{}".format(
    end_total_asset, strategy_income, strategy_income_rate, annualized_income_rate, win_rate * 100, trade_times))

# 处理数据用于绘图
daily_total_assets_df = pd.DataFrame(daily_total_assets, columns=['日期', '总资产'])
daily_income_rates_df = pd.DataFrame(daily_income_rates, columns=['日期', '收益率'])
sell_income_rates = [record[7] for record in trade_records if len(record) > 7]

# 将日期列转换为datetime类型
daily_total_assets_df['日期'] = pd.to_datetime(daily_total_assets_df['日期'])
daily_income_rates_df['日期'] = pd.to_datetime(daily_income_rates_df['日期'])

# 创建一个包含三个子图的图形
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

# 绘制总资产
ax1.plot(daily_total_assets_df['日期'], daily_total_assets_df['总资产'], label='daily_total_assets')
ax1.axhline(y=100000, color='r', linestyle='--', label='initial_money')
ax1.set_title('总资产')
ax1.set_ylabel('总资产金额')
ax1.legend()
ax1.tick_params(axis='x', rotation=45)

# 绘制资产收益率
ax2.plot(daily_income_rates_df['日期'], daily_income_rates_df['收益率'], label='daily_income_rates')
ax2.axhline(y=0, color='r', linestyle='--', label='0%')
ax2.set_title('资产收益率')
ax2.set_ylabel('收益率')
ax2.legend()
ax2.tick_params(axis='x', rotation=45)

# 绘制交易收益率
ax3.plot(sell_income_rates, label='sell_income_rate')
ax3.axhline(y=0, color='r', linestyle='--', label='0%')
ax3.set_title('交易收益率')
ax3.set_xlabel('交易序号')
ax3.set_ylabel('收益率')
ax3.legend()

plt.show()
