# CONTAINS ALL TRADING LOGIC APPLIED IN THE BOT

from technicalIndicators import *

def macd(history, symbol):
    # Args: Dataframe with history of the stock, the stock symbol
    # Return: Either SELL, BUY or PASS, indicating what action to take

    ema26 = ema(history['Close'], 26)
    ema12 = ema(history['Close'], 12)

    lenDiff = len(ema12) - len(ema26)
    macds = []
    for j in range(len(ema26)):
        macds.append(ema12[j + lenDiff] - ema26[j])

    signalLine = ema(macds, 9)

    if (macds[-1] < signalLine[-1] and macds[-2] > signalLine[-2]): # MACD crossed below signal
        result = "SELL"
    elif (macds[-1] > signalLine[-1] and macds[-2] < signalLine[-2]): # MACD crossed above signal line
        result = "BUY"
    else:
        result = "PASS"

    return result

def tradingLogic(history, symbol):
    # This function should ALWAYS be used when trading stocks to make sure the same logic is used for buying
    # and selling. The logic used should be modified in their separate functions and applied here.

    # Args: Dataframe with history of the stock, the stock symbol
    # Return: Either SELL, BUY or PASS, indicating what action to take

    return macd(history, symbol)