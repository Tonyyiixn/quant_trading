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

class TestStrategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        # runs every bar
        print(f'Close: {self.data.close[0]}')

class RSI_Strategy(bt.Strategy):
    params = (('rsi_period', 14), ('rsi_overbought', 70), ('rsi_oversold', 30),)

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy()
        else:
            if self.rsi > 70:
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
cerebro.addstrategy(RSI_Strategy)
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())    
cerebro.plot()