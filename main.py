# THE MAIN FILE THAT RUNS THE BOT

import alpaca_trade_api as alpaca
import yfinance as yfinance
import pandas as pandas
import numpy as numpy
from bs4 import BeautifulSoup
import string
import requests
from alpacaKeys import alpaca_key_id, alpaca_secret_key
from tradingLogic import tradingLogic

# Alpaca creds and api
key_id = alpaca_key_id
secret_key = alpaca_secret_key

# Initialize the alpaca api
base_url = "https://paper-api.alpaca.markets"

alpacaApi = alpaca.REST(
    key_id,
    secret_key,
    base_url,
    'v2'
    )

def scanPortfolio():
    # Get all current stocks in the portfolio
    # Get history for each stock
    # Decide whether to sell or keep
    # Execute any sell orders

    positions = alpacaApi.list_positions()
    symbol, qty, marketValue = [], [], []

    for each in positions:
        symbol.append(each.symbol)
        qty.append(int(each.qty))
        marketValue.append(float(each.market_value))

    portfolioDF = pandas.DataFrame(
        {
            'symbol': symbol,
            'qty': qty,
            'marketValue': marketValue
        }
    )

    for i in range(len(portfolioDF['symbol'])):
        symbol = portfolioDF.iloc[i]['symbol']
        history = yfinance.download(symbol, period="3mo") # 3 month period of data
        history = history.loc[~history.index.duplicated(keep='first')]

        try:
            action = tradingLogic(history, symbol)

            if (action == "SELL"):
                alpacaApi.submit_order(
                    symbol=symbol,
                    qty=int(portfolioDF.iloc[i]['qty']),
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print("SOLD: " + symbol)
            else:
                print("KEPT: " + symbol)

        except (IndexError, TypeError) as e:
            pass

    return

def findStocks(numDesiredStocks, market):
    # Scrape eoddata.com for all stock symbols in NYSE
    # Retrieve data for all stocks through yfinance
    # Analyze the stock data to decide which stocks to buy
    # Execute any buy orders

    #Args: Desired number of different stocks to own, stock market

    alphabet = list(string.ascii_uppercase)

    symbols = []

    # Loop through the letters in the alphabet to get the stocks on each page
    # from the table and store them in a list
    for each in alphabet:
        url = 'http://eoddata.com/stocklist/' + market + '/{}.htm'.format(each)
        response = requests.get(url)
        site = response.content
        soup = BeautifulSoup(site, 'html.parser')
        table = soup.find('table', {'class': 'quotes'})
        for row in table.findAll('tr')[1:]:
            symbol = row.findAll('td')[0].text.rstrip()
            realStock = True
            for letter in symbol:
                if (letter == '-' or letter == '.'):
                    realStock = False
                    break
            
            if (realStock):
                symbols.append(symbol)

        print("----- " + each + " STOCKS SCRAPED -----")

    # Download data for all symbols
    symbolString = ""
    for symbol in symbols:
        if (symbolString == ""):
            symbolString = symbolString + symbol    
        else:
            symbolString = symbolString + " " + symbol
    data = yfinance.download(symbolString, period="3mo", group_by="ticker")

    # Find potential stocks to buy
    potentialBuys = []
    for i in range(len(symbols)):
        # yfinance API sometimes return duplicate dates when querying multiple stocks, this keeps one copy
        history = data[symbols[i]].loc[~data[symbols[i]].index.duplicated(keep='first')]
        # ... and sometimes the first row is NaN, so we delete it
        history = history.drop(history.index[0])

        try:
            action = tradingLogic(history, symbols[i])
            if (action == "BUY"):
                potentialBuys.append((symbols[i], history))
        except (IndexError, TypeError) as e:
            pass

    # Buy the stock(s)
    buyingPower = float(alpacaApi.get_account().buying_power) * 0.9
    numStocksToBuy = numDesiredStocks - len(alpacaApi.list_positions())
    for stock in potentialBuys:
        symbol = stock[0]
        history = stock[1]

        if (numStocksToBuy <= 0):
            break

        qty = int((buyingPower / numStocksToBuy) / history['Close'][-1])

        if (qty > 0):
            try:
                alpacaApi.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print("BOUGHT " + str(qty) + " " + symbol)
                numStocksToBuy -= 1
                buyingPower -= qty * history['Close'][-1]
            except alpaca.rest.APIError:
                pass
    
    return

def main():
    # The main function to run the bot

    # Settings
    numDesiredStocks = 8
    market = "NYSE"

    orders = alpacaApi.list_orders()

    if (len(orders) == 0):
        scanPortfolio()
        findStocks(numDesiredStocks, market)
    else:
        print("Waiting for previous orders to complete")

    return

main()
