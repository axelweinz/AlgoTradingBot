# CONTAINS FUNCTIONS FOR CALCULATING TECHNICAL INDICATORS

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