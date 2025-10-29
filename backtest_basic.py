import backtrader as bt

def tdx_sma(price_list,N,M):
    """
    This is a function to calculate the TDX-style Simple Moving Average (SMA).
    price_list: the list of prices 
    N: the period of the SMA
    M: the weight factor
    return: a list of SMA values
    """
    sma_list = []
    for i in range(len(price_list)):
        if i == 0:
            sma_list.append(price_list[0])
        else:
            sma_value = (M * price_list[i] + (N - M) * sma_list[i - 1]) / N
            sma_list.append(sma_value)
    return sma_list

def tdx_ema(price_list, N):
    """
    This is a function to calculate the TDX-style Exponential Moving Average (EMA).
    price_list: the list of prices 
    N: the period of the EMA
    return: a list of EMA values
    """
    ema_list = []
    multiplier = 2 / (N + 1)
    for i in range(len(price_list)):
        if i == 0:
            ema_list.append(price_list[0])
        else:
            ema_value = (price_list[i] - ema_list[i - 1]) * multiplier + ema_list[i - 1]
            ema_list.append(ema_value)
    return ema_list

def tdx_ma(price_list, N):
    """
    This is a function to calculate the TDX-style Moving Average (MA).
    price_list: the list of prices 
    N: the period of the MA
    return: a list of MA values
    """
    ma_list = []
    for i in range(len(price_list)):
        if i < N - 1:
            ma_list.append(sum(price_list[:i + 1]) / (i + 1))
        else:
            ma_value = sum(price_list[i - N + 1:i + 1]) / N
            ma_list.append(ma_value)
    return ma_list

class LWR_Indicator(bt.Indicator):
    lines = ('lwr1','lwr2')
    params = (('N', 14),('M1', 3),('M2', 3),)

    def __init__(self):
        self.addminperiod(self.params.N)
        self.rsv_list = []
    def next(self):
        highest_high = max(self.data.high.get(size=self.params.N))
        lowest_low = min(self.data.low.get(size=self.params.N))
        if highest_high == lowest_low:
            rsv = 0
        else:
            rsv = (highest_high - self.data.close[0]) / (highest_high - lowest_low) * 100
        
        self.rsv_list.append(rsv)

        lwr1_list = tdx_sma(self.rsv_list, self.params.M1, 1)
        lwr2_list = tdx_sma(lwr1_list, self.params.M2, 1)   
        
        self.lines.lwr1[0] = lwr1_list[-1]
        self.lines.lwr2[0] = lwr2_list[-1]

class TestStrategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        # runs every bar
        print(f'Close: {self.data.close[0]}')

class LWR_Strategy(bt.Strategy):
    params = (('N', 14), ('M1', 3), ('M2', 3))

    def __init__(self):
        self.lwr = LWR_Indicator(
            self.data, 
            N=self.params.N, 
            M1=self.params.M1, 
            M2=self.params.M2
        )

    def next(self):
        close = self.data.close[0]
        lwr1 = self.lwr.lwr1[0]
        lwr2 = self.lwr.lwr2[0]

        if lwr1 is None or lwr2 is None:
            return
        
        if not self.position:
            if lwr2 < 20:
                self.buy()
        else:
            if lwr2 > 80:
                self.sell()

cerebro = bt.Cerebro()

data = bt.feeds.GenericCSVData(
    dataname='export/SH#600021.txt',
    dtformat=('%Y-%m-%d'),
    timeframe=bt.TimeFrame.Days,
    separator='\t',
    encoding='gbk',
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1
)

cerebro.adddata(data)
cerebro.addstrategy(LWR_Strategy)
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())    
cerebro.plot()