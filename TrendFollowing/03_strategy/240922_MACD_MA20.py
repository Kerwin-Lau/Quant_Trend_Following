import akshare as ak
import pandas as pd
import talib

# 以下配置代码请勿删除
# 回测区间
bt_offset_date = "20211201"
bt_start_date = "20220101"
bt_end_date = '20240921'
bt_data_adjust = "qfq"
# 回测股票数据集
bt_file_path = r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\StockPoolRandom.csv'
bt_stcckpool = pd.read_csv(bt_file_path, dtype={'代码': str})
# 新增3列'持仓数量'和'交易收益'，并填充为0
bt_stcckpool.loc[:, ['持仓数量', '累计交易收益','累计交易手续费']] = 0
print(bt_stcckpool)
# 初始资金及头寸数量配置
initial_money = 100000
position_num = 10
position_size = initial_money / position_num
remain_money = initial_money
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

# 策略回测
# 依次对stockpool中的股票进行策略回测

# step1: 根据回测区间，获取交易日数据
#   带offset交易日数据
trading_date_offset = ak.stock_zh_a_hist(symbol="603786", period="daily", start_date=bt_offset_date, end_date=bt_end_date, adjust=bt_data_adjust)
trading_date_offset = trading_date_offset.iloc[:, 0]
#   将第一列数据转换为 str 数据类型,删除第一列数据中的连接符 '-' 并存储这些数据
trading_date_offset = trading_date_offset.astype(str)
trading_date_offset= trading_date_offset.str.replace('-', '')
#   无offset交易日数据
trading_date = ak.stock_zh_a_hist(symbol="603786", period="daily", start_date=bt_start_date, end_date=bt_end_date, adjust=bt_data_adjust)
trading_date = trading_date.iloc[:, 0]
#   将第一列数据转换为 str 数据类型,删除第一列数据中的连接符 '-' 并存储这些数据
trading_date = trading_date.astype(str)
trading_date= trading_date.str.replace('-', '')
# 保存结果
trading_date_offset.to_csv(r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\trading_date_offset.csv', index=False)
trading_date.to_csv(r'D:\Quant\01_SwProj\02_TrendFollowing\Quant_Trend_Following\TrendFollowing\02_data\trading_date', index=False)
# 打印结果
print(trading_date_offset)
print(trading_date)

# step2: 从回测区间的第一个交易日开始，每个交易日依次进行回测
for i in range(0, len(trading_date)):

    print(trading_date[i])

    # 单日个股回测循环
    for j in range(0, len(bt_stcckpool)):
        print(bt_stcckpool.iloc[j]['代码'])
        # step3：获取当前交易日的个股数据
        # MA20均线策略-专用数据获取
        his_stockdata_em = ak.stock_zh_a_hist(symbol=bt_stcckpool.iloc[j]['代码'], period="daily",start_date=trading_date_offset[i], end_date=trading_date[i], adjust=bt_data_adjust)
        #如果此股票在回测区间内没有数据，跳出循环
        if his_stockdata_em.empty:
            print("no data")
            continue
        # 计算回测数据中中今天的数据index
        bt_today_index = len(his_stockdata_em)-1
        # 计算MA20指标
        his_stockdata_em['MA20'] = his_stockdata_em['收盘'].rolling(window=20).mean()
        # 提取收盘价数据
        close_prices = his_stockdata_em['收盘'].astype(float).values
        # MACD趋势反转策略-专用数据源获取
        his_stockdata_sina = ak.stock_zh_a_daily(symbol=bt_stcckpool.iloc[j]['代码_spot'], start_date=trading_date_offset[i],end_date=trading_date[i], adjust=bt_data_adjust)
        # 计算 MACD 指标
        macd, macd_signal, macd_histogram = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)

        # step4： 根据数据判断买入条件
        # 买入策略：
        # 1.未持有该支股票；
        # 2.MA20均线策略：前天收盘价低于MA20均线，昨天收盘价高于MA20均线，且昨天成交量较前天增加10%；
        # 3.MACD反转策略：前天收盘时MACD低于MACD Signal，昨天收盘MACD高于MACD Signal，且MACD Histogram为正数
        # buy condition 1
        if bt_stcckpool.iloc[j]['持仓数量'] == 0:
            buy_cdn1 = 1
        else:
            buy_cdn1 = 0
        # buy condition 2
        print(his_stockdata_em['收盘'].iloc[bt_today_index-1])
        print(his_stockdata_em)
        if his_stockdata_em['收盘'].iloc[bt_today_index - 2] <= his_stockdata_em['MA20'].iloc[bt_today_index - 2] and \
                his_stockdata_em['收盘'].iloc[bt_today_index - 1] > his_stockdata_em['MA20'].iloc[bt_today_index - 1] and \
                his_stockdata_em['成交量'].iloc[bt_today_index - 1] > 1.1 * his_stockdata_em['成交量'].iloc[bt_today_index - 2]:
            buy_cdn2 = 1
        else:
            buy_cdn2 = 0
        # buy condition 3
        if macd[bt_today_index - 2] < macd_signal[bt_today_index - 2] and macd[bt_today_index - 1] > macd_signal[bt_today_index - 1] and macd_histogram[bt_today_index - 1] > 0:
            buy_cdn3 = 1
        else:
            buy_cdn3 = 0
        print(buy_cdn1, buy_cdn2, buy_cdn3)
        
        # # step5：组合买入判断条件，决定是否买入
        # if buy_cdn1 and (buy_cdn2 or buy_cdn3):
        #     buy_price = his_stockdata_em['开盘'].iloc[j]
        #     can_buy_num = position_size // buy_price
        #     # 每次最少买100股
        #     real_buy_num = (can_buy_num // 100) * 100
        #     if real_buy_num < 100:
        #         real_buy_num = 0
        #     if real_buy_num > 0 and remain_money > position_size:
        #         cost = real_buy_num * buy_price
        #         bt_stcckpool.loc[bt_stcckpool.index[i], '持仓数量'] += real_buy_num
        #         remain_money -= cost
        #         buy_cost_price = cost / real_buy_num if real_buy_num else 0
        #         last_buy_price = buy_price
        #         buy_date = his_stockdata_em['日期'].iloc[i]
        #         trade_records.append([buy_date, '买', real_buy_num, buy_price,
        #                               initial_money + bt_stcckpool.iloc[i]['持仓数量'] * his_stockdata_em['收盘'].iloc[
        #                                   i],
        #                               bt_stcckpool.iloc[i]['持仓数量'] * his_stockdata_em['收盘'].iloc[i],
        #                               initial_money])


