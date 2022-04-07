import pandas as pd
import pandas_datareader as pdr
import numpy as np
import datetime
import time
import math
money = 0
class Stock:
    def __init__(self,symbol,count):
        self.return_value = 0
        self.difference = 0
        # self.trend = 0
        self.price = 0
        self.last_price = self.price
        self.count = count
        self.symbol = symbol
        self.lowest_stock = False
        self.last_sold = False
        self.mean = 0

    def get_values(self,day):
        start = datetime.datetime(2020, 12, 1)
        stock_prices = pd.DataFrame(pdr.get_data_yahoo(self.symbol,start,day)['Close'])
        
        stock_prices['20d'] = stock_prices['Close'].rolling(window=20).mean()
        
        stock_prices['return'] = np.log(stock_prices['Close'] / stock_prices['Close'].shift(1))
        
        stock_prices['difference'] = stock_prices['Close'] - stock_prices['20d']
        
        stock_prices['hold'] = np.where(stock_prices['difference'] < -3, 1, np.nan)
        stock_prices['hold'] = np.where(stock_prices['difference'] * stock_prices['difference'].shift(1) < 0, 0, stock_prices['hold'])
        
        stock_prices['hold'] = stock_prices['hold'].ffill().fillna(0)
        stock_prices['gain_loss'] = stock_prices['hold'].shift(1) * stock_prices['return']
        stock_prices = stock_prices.dropna(subset=['20d'])
        
        stock_prices['total'] = stock_prices['gain_loss'].cumsum()
    
        stock_return = stock_prices['return'].to_numpy()
        stock_difference = stock_prices['difference'].to_numpy()
        stock_price = stock_prices['Close'].to_numpy()
        stock_trend = stock_prices['difference'].to_numpy()
        stock_mean = stock_prices['20d'].to_numpy()
    
        self.return_value = stock_return[-1]
        self.difference = stock_difference[-1]
        self.price = stock_price[-1]
        self.mean = stock_mean[-1]
        # self.trend = stock_trend[-10:].mean()
        
    def sell(self):
        global money
        if self.price >= self.mean * 1.04 or self.price <= self.mean * 0.7:
            money += self.count * self.price
            old = self.count
            self.count = 0
            print("Sold", old,self.symbol, "Current Balance:",money)
            if self.price <= self.mean * 0.8:
                self.last_sold = True
            return True
        return False
        
    def buy(self,refresh_sold):
        global money
        purchase_size = math.floor(money / self.price)
        money -= purchase_size * self.price
        self.count += purchase_size
        for i in refresh_sold:
            i.last_sold = False
        self.last_sold = True
        print("Bought",self.count, self.symbol)



def execute(stocks,day):
    #buy and sell logic
    need_new = False
    change_in_money = 0
    first_loop = True
    money_points = []
    starting_balance = 0
    for i in stocks:
        i.get_values(day[0])
        starting_balance += i.count * i.price
    portfolio = starting_balance
    for k in day:
        for i in stocks:
            i.get_values(k)

        for i in stocks:
            if i.count > 0:
                portfolio = i.price * i.count + money

        for i in stocks:
            if i.count > 0 and not first_loop:
                change_in_money = (portfolio - starting_balance)
                print("Stock Price:",int(i.price),"Stock Mean:", int(i.mean),"Money Earned:",int(change_in_money),"Portfolio:",int(portfolio))
            elif i.count > 0 and first_loop:
                first_loop = False
                print("Stock Price:",int(i.price),"Stock Mean:", int(i.mean),"Money Earned:",int(change_in_money),"Portfolio:",int(portfolio))

        for i in stocks:
            if i.count > 0:
                if not need_new:
                    need_new = i.sell()
                    
        if need_new:
            lowest_trend = math.inf
            for i in stocks:
                if i.last_sold == False:
                    if i.difference < lowest_trend and i.price < i.mean and money > i.price:
                        for j in stocks:
                            j.lowest_stock = False
                        lowest_trend = i.difference
                        i.lowest_stock = True
            for i in stocks:
                if i.lowest_stock == True and i.last_sold == False:
                    i.buy(stocks)
                    need_new = False
        for i in stocks:
            if i.count > 0:
                money_points.append(i.price * i.count + money)

    return i.count, i.symbol, i.price, change_in_money, money, money_points

            
