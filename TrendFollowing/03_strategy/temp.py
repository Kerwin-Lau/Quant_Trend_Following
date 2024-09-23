 # 获取股票数据
    # MA20均线策略-专用数据获取
    his_stockdata_em = ak.stock_zh_a_hist(symbol=bt_stcckpool.iloc[i]['代码'], period="daily", start_date=bt_start_date,end_date=bt_end_date,adjust=bt_data_adjust)
    print(his_stockdata_em)
    # MACD趋势反转策略-专用数据源获取
    his_stockdata_sina = ak.stock_zh_a_daily(symbol=bt_stcckpool.iloc[i]['代码_spot'], start_date=bt_start_date, end_date=bt_end_date, adjust=bt_data_adjust)
    # 提取收盘价数据
    close_prices = his_stockdata_em['收盘'].astype(float).values
    # 计算 MACD 指标
    macd, macd_signal, macd_histogram = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    # 计算MA20指标
    his_stockdata_em['MA20'] = his_stockdata_em['收盘'].rolling(window=20).mean()
    # print(bt_stcckpool.iloc[i]['代码_spot'])
    # print(his_stockdata_em)
    # print(his_stockdata_sina)
    for j in range(2, len(his_stockdata_em)):
        # 买入条件判断
        #1.未持有该支股票
        if bt_stcckpool.iloc[i]['持仓数量']==0:
            buy_cdn1 = 1
        else:
            buy_cdn1 = 0
        # 2.MA20均线策略：前天收盘价低于MA20均线，昨天收盘价高于MA20均线，且昨天成交量较前天增加10%
        if his_stockdata_em['收盘'].iloc[j - 2] <= his_stockdata_em['MA20'].iloc[j - 2] and \
            his_stockdata_em['收盘'].iloc[j - 1] > his_stockdata_em['MA20'].iloc[j - 1] and \
            his_stockdata_em['成交量'].iloc[j - 1] > 1.1 * his_stockdata_em['成交量'].iloc[j - 2]:
            buy_cdn2 = 1
        else:
            buy_cdn2 = 0
        # 3.MACD反转策略：前天收盘时MACD低于MACD Signal，昨天收盘MACD高于MACD Signal，且MACD Histogram为正数
        if macd[j - 2] < macd_signal[j - 2] and macd[j - 1] > macd_signal[j - 1] and macd_histogram[j - 1] > 0:
            buy_cdn3 = 1
        else:
            buy_cdn3 = 0

    #     组合判断条件，决定是否买入
        if buy_cdn1 and (buy_cdn2 or buy_cdn3):
            buy_price = his_stockdata_em['开盘'].iloc[j]
            can_buy_num = position_size // buy_price
            # 每次最少买100股
            real_buy_num = (can_buy_num // 100) * 100
            if real_buy_num < 100:
                real_buy_num = 0
            if real_buy_num > 0 and remain_money > position_size:
                cost = real_buy_num * buy_price
                bt_stcckpool.loc[bt_stcckpool.index[i], '持仓数量'] += real_buy_num
                remain_money -= cost
                buy_cost_price = cost / real_buy_num if real_buy_num else 0
                last_buy_price = buy_price
                buy_date = his_stockdata_em['日期'].iloc[i]
                trade_records.append([buy_date, '买', real_buy_num, buy_price,
                                      initial_money + bt_stcckpool.iloc[i]['持仓数量'] * his_stockdata_em['收盘'].iloc[i],
                                      bt_stcckpool.iloc[i]['持仓数量'] * his_stockdata_em['收盘'].iloc[i], initial_money])


# 股票数量
stock_num = 0


# 获取股票数据
stock_data = ak.stock_zh_a_daily(symbol="sh603768", start_date="20230101", end_date="20240922", adjust="qfq")

# 提取收盘价数据
close_prices = stock_data['close'].astype(float).values

# 计算 MACD 指标
macd, macd_signal, macd_histogram = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)

# for i in range(1, len(stock_data)):
#     yesterday_macd = macd[i - 1]
#     today_macd = macd[i]
#     yesterday_signal = macd_signal[i - 1]
#     today_signal = macd_signal[i]
#     yesterday_histogram = macd_histogram[i - 1]
#     today_histogram = macd_histogram[i]
#
#     if yesterday_macd < yesterday_signal and today_macd > today_signal and today_histogram > 0:
#         # 买入条件满足，使用 1 寸头资金以开盘价买入
#         buy_price = stock_data.iloc[i]['open']
#         buy_amount = position_size / buy_price
#         # 每次最少买 100 股
#         real_buy_num = (buy_amount // 100) * 100
#         if real_buy_num < 100:
#             real_buy_num = 0
#         if real_buy_num > 0:
#             cost = real_buy_num * buy_price
#             stock_num += real_buy_num
#             initial_money -= cost
#             buy_cost_price = cost / real_buy_num if real_buy_num else 0
#             last_buy_price = buy_price
#             trade_records.append(f"Buy on {stock_data.index[i]} at price {buy_price}. Quantity: {real_buy_num}. New stock count: {stock_num}. Remaining money: {initial_money}.")
#             buy_date = stock_data.index[i]
#             can_sell = False
#
#     elif (yesterday_macd > yesterday_signal and today_macd < today_signal) or (yesterday_histogram > 0 and today_histogram < 0 and stock_num > 0):
#         # 卖出条件满足，以开盘价卖出股票
#         sell_price = stock_data.iloc[i]['open']
#         sold_amount = stock_num
#         stock_num = 0
#         profit = sold_amount * (sell_price - buy_cost_price)
#         trade_records.append(f"Sell on {stock_data.index[i]} at price {sell_price}. Quantity sold: {sold_amount}. New stock count: {stock_num}. Profit: {profit}.")
#
# # 计算总资产（包含股票市值和剩余资金）
# for i in range(len(stock_data)):
#     total_asset = stock_num * stock_data['close'].iloc[i] + initial_money
#     daily_total_assets.append([stock_data.index[i], total_asset])
#     income_rate = (total_asset - 100000) / 100000 * 100
#     daily_income_rates.append([stock_data.index[i], income_rate])
#
# # 打印交易信息
# trade_times = len([record for record in trade_records if record[1] in ['买', '卖']]) // 2
# win_count = 0
# for record in trade_records:
#     if len(record) == 7:
#         try:
#             # 尝试将相关字段转换为数字类型
#             num_record = [float(item) if item.replace('.', '', 1).isdigit() else item for item in record]
#             print("日期：{}，操作：{}，数量：{}，成交价格：{}，总资产：{}，持有市值：{}，闲置资金：{}".format(num_record[0], num_record[1], num_record[2], num_record[3],
#                                                                                   round(num_record[4], 2), round(num_record[5], 2),
#                                                                                   round(num_record[6], 2)))
#         except ValueError:
#             print("日期：{}，操作：{}，数量：{}，成交价格：{}，总资产：{}，持有市值：{}，闲置资金：{}".format(record[0], record[1], record[2], record[3],
#                                                                                   record[4], record[5], record[6]))
#     else:
#         if len(record) > 7:
#             try:
#                 if float(record[7]) > 0:
#                     win_count += 1
#                 num_record = [float(item) if item.replace('.', '', 1).isdigit() else item for item in record]
#                 print("日期：{}，操作：{}，数量：{}，成交价格：{}，总资产：{}，持有市值：{}，闲置资金：{}，卖出收益率：{:.2f}%".format(
#                     num_record[0], num_record[1], num_record[2], num_record[3], round(num_record[4], 2), round(num_record[5], 2), round(num_record[6], 2),
#                     float(num_record[7])))
#             except ValueError:
#                 pass