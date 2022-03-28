import websocket, json, pprint, numpy #talib
# import config
# from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 4
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 25
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True
    
def RSI_Calculating():
    gains = []
    losses = []
    window = []

    prev_avg_gain = None
    prev_avg_loss = None

    for i, price in enumerate(closes):
        if i == 0:
            window.append(price)
            continue

        difference = round(closes[i] - closes[i - 1], 2)

        if difference > 0:
            gain = difference
            loss = 0
        elif difference < 0:
            gain = 0
            loss = abs(difference)
        else:
            gain = 0
            loss = 0
        gains.append(gain)
        losses.append(loss)
        if i < RSI_PERIOD:
            window.append(price)
            continue

        if i == RSI_PERIOD:
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)

        else:
            avg_gain = (prev_avg_gain * (RSI_PERIOD - 1) + gain) / RSI_PERIOD
            avg_loss = (prev_avg_loss * (RSI_PERIOD - 1) + loss) / RSI_PERIOD

        prev_avg_gain = avg_gain
        prev_avg_loss = avg_loss

        avg_gain = round(avg_gain, 2)
        avg_loss = round(avg_loss, 2)
        prev_avg_gain = round(prev_avg_gain, 2)
        prev_avg_loss = round(prev_avg_loss, 2)

        rs = round(avg_gain / avg_loss, 2)

        rsi = round(100 - (100 / (1 + rs)), 2)

    return rsi

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    # print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:


            rsi = RSI_Calculating()
            print("RSI {}".format(rsi))

            closes = closes[1:]    # update data

            # rsi = talib.RSI(np_closes, RSI_PERIOD)

            

            if rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    # order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    # if order_succeeded:
                    in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    # order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    # if order_succeeded:
                    in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
