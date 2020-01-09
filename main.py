import alpaca_trade_api as alpaca
import yfinance as yfinance
import pandas as pandas
import numpy as numpy

# Alpaca creds and api
#key_id = "YOUR KEY HERE"
#secret_key = "YOUR SECRET KEY HERE"

# Alpaca creds and api
key_id = "PKUTHT80SMHT7VSM9FR3"
secret_key = "YYA9xoHEipDib2VAwgMVJPlEe20vmYhvO15Dv7vU"

# Initialize the alpaca api
base_url = "https://paper-api.alpaca.markets"

alpacaApi = alpaca.REST(
    key_id,
    secret_key,
    base_url,
    'v2'
    )

def ema(values, window):
    # Args: Array of values, number of periods in ema
    # Return: Array of EMAs of every value after the initial SMA

    emas = []

    valuesSum = 0
    try:
        for i in range(window): # Calculate sma
            valuesSum += values[i]
    except IndexError:
        print("Window too large for closing price history.")
        return

    sma = valuesSum / window
    smoothing = 2 / (window + 1)

    prevEma = -1
    for i in range(window, len(values)): # Calculate ema

        if (i == window):        
            ema = values[i] * smoothing + sma * (1 - smoothing)
        else:
            ema = values[i] * smoothing + prevEma * (1 - smoothing)

        emas.append(ema)
        prevEma = ema

    return emas

def obv(closingPrices, closingVolumes):
    # Args: Array of closing prices, array of closing volumes
    # Return: Array of OBV's for each period

    obvs = []

    obv = 0
    for i in range(len(closingPrices)):
        if (i == 0):
            obv = 0
        elif (closingPrices[i] > closingPrices[i-1]):
            obv += closingVolumes[i]
        elif (closingPrices[i] < closingPrices[i-1]):
            obv -= closingVolumes[i]

        obvs.append(obv)

    return obvs

def rsi(closingPrices, currPrice, window):
    # Args: Array of previous closing prices, current stock price, number of periods in rsi
    # Return: RSI of current price

    totUp = 0
    totDown = 0
    try:
        for i in range(1, window + 1): # Calculate starting avgUp/avgDown
            if (closingPrices[i] > closingPrices[i-1]):
                totUp += (closingPrices[i] - closingPrices[i-1]) / closingPrices[i-1]
            elif (closingPrices[i] < closingPrices[i-1]):
                totDown += (closingPrices[i-1] - closingPrices[i]) / closingPrices[i-1]
    except IndexError:
        print("Window too large for closing price history.")
        return

    avgUp = totUp / window
    avgDown = totDown / window

    currUp = 0
    currDown = 0
    for i in range(window + 1, len(closingPrices)): # Calculate avgUp/avgDown with smoothing
        if (closingPrices[i] > closingPrices[i-1]):
            currUp = (closingPrices[i] - closingPrices[i-1]) / closingPrices[i-1]
        elif (closingPrices[i] < closingPrices[i-1]):
            currDown = (closingPrices[i-1] - closingPrices[i]) / closingPrices[i-1]
        
        avgUp = (avgUp * (window - 1) + currUp) / window
        avgDown = (avgDown * (window - 1) + currDown) / window
        currUp = 0
        currDown = 0

    if (currPrice > closingPrices[-1]): # Calculate current price change
        currUp = (currPrice - closingPrices[-1]) / closingPrices[-1]
    elif (currPrice < closingPrices[-1]):
        currDown = (closingPrices[-1] - currPrice) / closingPrices[-1]

    if (avgDown == 0): # Prevent division by zero
        rsi = 100
    else:
        rsi = 100 - (100 / (1 + ((avgUp * (window - 1) + currUp) / (avgDown * (window - 1) + currDown))))

    return rsi

def scanPortfolio():
    # CURRENTLY USES MACD 26/12 TRADING STRATEGY
    
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
            ema26 = ema(history['Close'], 26)
            ema12 = ema(history['Close'], 12)
                
            lenDiff = len(ema12) - len(ema26)
            macds = []
            for i in range(len(ema26)):
                macds.append(ema12[i + lenDiff] - ema26[i])
            
            signalLine = ema(macds, 9)

            # Sell if macd crosses below signal line
            if (macds[-1] < signalLine[-1]):
                # alpacaApi.submit_order(
                #     symbol=symbol,
                #     qty=
                # )
                print("SOLD: " + symbol)
            else:
                print("NOT SOLD: " + symbol)

        except TypeError: # Too few values in the stock history for the window in EMA
            pass

    return

#test1 = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03,
    #46.41, 46.22, 45.64, 46.21, 46.25, 45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66]
#test3 = [10, 10.15, 10.17, 10.13, 10.11, 10.15, 10.20, 10.20, 10.22, 10.21]
#test4 = [25200, 30000, 25600, 32000, 23000, 40000, 36000, 20500, 23000, 27500]
#data = yfinance.download("GOOGL", start="2020-01-01", end="2020-01-07")
#print(data)
scanPortfolio()