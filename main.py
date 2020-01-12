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
        history = (yfinance.download(symbol, period="3mo")) # 3 month period of data

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

        except TypeError: # Too few values in the stock history for the window in EMA
            pass

    return

def findStocks():
    # Scrape eoddata.com for all stock symbols in NYSE
    # Retrieve data for all stocks through yfinance
    # Analyze the stock data to decide which stocks to buy

    alphabet = list(string.ascii_uppercase)

    symbols = []

    # Loop through the letters in the alphabet to get the stocks on each page
    # from the table and store them in a list
    for each in alphabet:
        url = 'http://eoddata.com/stocklist/NYSE/{}.htm'.format(each)
        response = requests.get(url)
        site = response.content
        soup = BeautifulSoup(site, 'html.parser')
        table = soup.find('table', {'class': 'quotes'})
        for row in table.findAll('tr')[1:]:
            symbols.append(row.findAll('td')[0].text.rstrip())

    # Now retrieve data for all symbols through yfinance...


    return symbols

#test1 = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03,
    #46.41, 46.22, 45.64, 46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66]
#test3 = [10, 10.15, 10.17, 10.13, 10.11, 10.15, 10.20, 10.20, 10.22, 10.21]
#test4 = [25200, 30000, 25600, 32000, 23000, 40000, 36000, 20500, 23000, 27500]
#history = yfinance.download("GOOGL", start="2020-01-01", end="2020-01-07")
#print(tradingLogic(history, "GOOGL"))
symbols = findStocks()
print(symbols[-1])