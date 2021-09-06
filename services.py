import pandas as pd
import numpy as np
import datetime as dt
import math
from dataclasses import dataclass, field


@dataclass
class CashManager:
    available_cash: float
    # Default values for dataclasses cannot be mutable objects for data protection purposes when multiple instances of the class are created. 
    # field(default_factory=list) is a workaround to create multiple instances that have a cash_history list pointing to differents memory adresses
    cash_history: list = field(default_factory=list)

    def __post_init__(self):
        #Default value for cash_history
        self.cash_history = [['ticker', 'date', 'price', 'qty', 'amount', 'available_cash', 'order', 'total_qty']] 
    
    def upgrade_cash_history(self, ticker, date, price, qty, order, total_qty):
        amount = np.round(price*qty, 2)
        self.available_cash = np.round(self.available_cash - amount, 2)
        self.cash_history.append([ticker, date, price, qty, -amount, self.available_cash, order, total_qty])

@dataclass
class Stock:
    ticker: str
    df: pd.DataFrame
    cash_manager: CashManager
    amount_trade: float
    date_last_buy: dt.datetime = dt.datetime.today()
    qty: int = 0

    def first_check(self) -> bool:
        return True if self.cash_manager.available_cash >= self.amount_trade else False

    def buy_stock(self, price, date):
        if self.qty == 0:
            buy_qty = math.floor(self.amount_trade/price)
            self.qty = buy_qty
            self.cash_manager.upgrade_cash_history(self.ticker, date, price, buy_qty, 'BUY', self.qty)
            self.date_last_buy = date

    def sell_stock(self, price, date):
        if self.qty > 0:
            sell_qty = -self.qty
            self.qty = 0
            self.cash_manager.upgrade_cash_history(self.ticker, date, price, sell_qty, 'SELL', self.qty)



class ReportData:
    # trading_histories type between strings because of some py version incompatibility
    def __init__(self, trading_histories: 'list[pd.DataFrame]', days_timespan: int):
        self.trading_histories = trading_histories
        self.days_timespan = days_timespan
        self.buys_dfs = self.total_buys()
        
    def strategies_profit(self) -> pd.DataFrame:
        df_profit = pd.DataFrame()
        df_profit['strategy'] = [f"strategy {x+1}" for x in range(len(self.trading_histories))]
        df_profit['strategy'].iloc[-1] = 'Benchmark'
        df_profit['profit_amount'] = [np.round(x.available_cash.iloc[-1] - x.available_cash.iloc[0], 2) for x in self.trading_histories]
        df_profit['profit_perc'] = [np.round((x.available_cash.iloc[-1]/x.available_cash.iloc[0]-1)*100, 2) for x in self.trading_histories]
        df_profit['APR'] = np.round(((df_profit['profit_perc']/100)*(365/self.days_timespan))*100, 2)
        df_profit['APY'] = np.round(((1+(df_profit['profit_perc'])/100)**(365/self.days_timespan)-1)*100, 2)
        return df_profit

    def total_buys(self) -> list:
        dfs = []
        for trading_history in self.trading_histories:
            df = pd.DataFrame()
            df['ticker'] = trading_history.ticker.unique()

            df['buys'] = [trading_history['order'][(trading_history['ticker'] == ticker) & (trading_history['order'] == 'BUY')].count() for ticker in df['ticker']]
            net_profit = []
            profitable_buys = []

            for ticker in df['ticker']:
                sell_price = trading_history['price'][(trading_history['ticker'] == ticker) & (trading_history['total_qty'] == 0)]
                buy_price = trading_history['price'][trading_history['ticker'] == ticker].shift(1)[trading_history['total_qty'] == 0]
                qty = trading_history['qty'][trading_history['ticker'] == ticker].shift(1)[trading_history['total_qty'] == 0]
                dif = (sell_price - buy_price)
                net_profit.append(np.round((dif*qty).sum(), 2))
                profitable_buys.append(dif[dif > 0].count())
            
            df['profitable_buys'] = profitable_buys
            df['net_profit'] = net_profit

            dfs.append(df)
        return dfs



    def most_bought_per_strat(self):
        return [df.sort_values(by='buys', ascending=False).head(5) for df in self.buys_dfs]


    def most_profit_per_strat(self):
        return [df.sort_values(by='net_profit', ascending=False).head(3) for df in self.buys_dfs]

    def most_bought_total(self):
        total_df = self.buys_dfs[0]
        df = pd.DataFrame()
        for buy_df in self.buys_dfs[1:-1]:
            total_df = pd.concat([total_df, buy_df], ignore_index=True)
        df['ticker'] = total_df.ticker.unique()
        df['buys'] = [total_df.buys[(total_df['ticker'] == ticker)].sum() for ticker in df.ticker]

        return df.sort_values(by='buys', ascending=False).head(5)
    
    def most_profit_total(self):
        total_df = self.buys_dfs[0]
        df = pd.DataFrame()
        for buy_df in self.buys_dfs[1:-1]:
            total_df = pd.concat([total_df, buy_df], ignore_index=True)
        df['ticker'] = total_df.ticker.unique()
        df['net_profit'] = np.round([total_df.net_profit[(total_df['ticker'] == ticker)].sum() for ticker in df.ticker], 2)
        
        return df.sort_values(by='net_profit', ascending=False).head(3)

    def generate_report(self):

        pass



def strategies(buy_perc: float, sell_perc: float, ratio: float, days: int) -> list:

    def strategy_1(stock, date):
        if stock.first_check():
            price: float = stock.df['price'][stock.df['date'] == date].iloc[-1]
            price_previous: float = stock.df['price'].shift(1)[stock.df['date'] == date].iloc[-1]
            var_perc: float = np.round(price/price_previous - 1, 4)
            if var_perc <= buy_perc:
                stock.buy_stock(price, date)
            if var_perc >= sell_perc:
                stock.sell_stock(price, date)

    def strategy_2(stock, date):
        if stock.first_check():
            price: float = stock.df['price'][stock.df['date'] == date].iloc[-1]
            average_price: float = stock.df['price'][stock.df['date'] < date].mean()
            days_since_last_buy: int = (date - stock.date_last_buy).days
            if price/average_price >= ratio:
                stock.buy_stock(price, date)
            if days_since_last_buy >= days:
                stock.sell_stock(price, date)

    def strategy_3(stock, date):
        if stock.first_check():
            price: float = stock.df['price'][stock.df['date'] == date].iloc[-1]
            price_previous: float = stock.df['price'].shift(1)[stock.df['date'] == date].iloc[-1]
            var_perc: float = np.round(price/price_previous - 1, 4)
            average_price: float = stock.df['price'][stock.df['date'] < date].mean()
            days_since_last_buy: int = (date - stock.date_last_buy).days
            if var_perc <= buy_perc and price/average_price >= ratio:
                stock.buy_stock(price, date)
            if var_perc >= sell_perc or days_since_last_buy >= 5:
                stock.sell_stock(price, date)
    
    def benchmark(stock, date):
        if len(stock.cash_manager.cash_history) > 1:
            tickers_unique = pd.DataFrame(stock.cash_manager.cash_history[1:], columns=stock.cash_manager.cash_history[0]).ticker.unique()
            if stock.ticker in tickers_unique:
                pass
            else: 
                date = stock.df.date.iloc[0]
                price: float = stock.df['price'][stock.df['date'] == date].iloc[-1]
                stock.buy_stock(price, date)
        else:
            date = stock.df.date.iloc[0]
            price: float = stock.df['price'][stock.df['date'] == date].iloc[-1]
            stock.buy_stock(price, date)

    return [strategy_1, strategy_2, strategy_3, benchmark]