import websocket, json, pprint
from binance.client import Client
from binance.enums import *
import config

socket = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

client = Client(config.API_KEY,config.API_SECRET, tld='us')

rsi_period = 14
rsi_ovB = 70
rsi_ovS = 30

trade_sym = 'ethusd'
trade_quant = 0.05

def order(symbol, quant, side, order_type=ORDER_TYPE_MARKET):
	try:
		order = client.create_order(symbol=symbol,
			side=side,
			type=order_type,
			quantity=quant)
		return True
	except Exception as e:
		print("an exception occured - {}".format(e))
		return False

def on_open(ws):
	print('opened connection')

def on_close(ws):
	print('closed connection')

def on_message(ws, message):
	global closes, in_position
	print('received message')
	#print(message)
	json_message = json.loads(message)
	pprint.pprint(json_message)

	candle = json_message['k']

	is_candle_closed = candle['x']
	close = candle['c']

	in_position = False

	if is_candle_closed:
		print('candle closed at {}'.format(close))
		closes.append(float(close))
		print('closes')
		print(closes)

		if len(closes) > rsi_period:
			np_closes = np.array(closes)
			rsi = talib.RSI(np.closes, rsi_period)
			print('All RSIs calculated so far')
			print(rsi)
			last_rsi = rsi[-1]
			print('the current rsi {}'.format(last_rsi))

			if last_rsi > rsi_ovB:
				if in_position:
					print('Sell!')
					order(trade_sym, trade_quant, SIDE_SELL)
					if order_succeeded:
						in_position = False

				else:
					print("We don't own any.")

			if last_rsi < rsi_ovS:
				if in_position:
					print('It is oversold but we already own it.')

				else:
					print('Buy!')
					order(trade_sym, trade_quant, SIDE_BUY)
					if order_succeeded:
						in_position = True

ws = websocket.WebSocketApp(socket,on_open=on_open,on_close=on_close,on_message=on_message)

ws.run_forever()