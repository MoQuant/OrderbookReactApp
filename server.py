#pip install websocket
#pip install websocket-client

# INSTALL: node.js, npm, npx, and create-react-app

import asyncio
import websockets
import websocket
import numpy as np
import json
import threading
import time

url = 'wss://ws-feed.exchange.coinbase.com'

class Data:

    bids = {}
    asks = {}

    sync = False
    no = 0

    def summation(self, depth=5):
        res = {}
        for tick in self.tickers:
            if tick in self.bids.keys() and tick in self.asks.keys():
                try:
                    bids = self.bids[tick]
                    asks = self.asks[tick]
                    bids = list(sorted(bids.items(), reverse=True))[:depth]
                    asks = list(sorted(asks.items()))[:depth]
                    
                    
                    bp, bv = np.array(bids).T.tolist()
                    ap, av = np.array(asks).T.tolist()
                    sum_bv = [float(np.sum(bv[:i])) for i in range(depth)]
                    sum_av = [float(np.sum(av[:i])) for i in range(depth)]
                    res[tick] = {'bid_x': bp[::-1], 'bid_y': sum_bv[::-1],
                                'ask_x': ap, 'ask_y':sum_av}
                except RuntimeError:
                    print("Runtime Error......")
        return res
        

    def parseBook(self, resp):
        if 'type' in resp.keys():
            if resp['type'] == 'snapshot':
                ticker = resp['product_id']
                self.bids[ticker] = {float(price):float(volume) for (price, volume) in resp['bids']}
                self.asks[ticker] = {float(price):float(volume) for (price, volume) in resp['asks']}
                self.no += 1
                if self.no == len(self.tickers):
                    self.sync = True
            if resp['type'] == 'l2update':
                ticker = resp['product_id']
                for (side, price, volume) in resp['changes']:
                    price, volume = float(price), float(volume)
                    if side == 'buy':
                        if volume == 0:
                            del self.bids[ticker][price]
                        else:
                            self.bids[ticker][price] = volume
                    if side == 'sell':
                        if volume == 0:
                            del self.asks[ticker][price]
                        else:
                            self.asks[ticker][price] = volume


        

class OBook(threading.Thread, Data):

    def __init__(self, tickers=['BTC-USD','ETH-USD']):
        threading.Thread.__init__(self)
        self.tickers = tickers

    def run(self):
        conn = websocket.create_connection(url)

        msg = {'type':'subscribe',
               'product_ids': self.tickers,
               'channels': ['level2']}

        conn.send(json.dumps(msg))

        while True:
            response = json.loads(conn.recv())
            self.parseBook(response)
            

class Server:

    def __init__(self, host='localhost', port=8080, tickers=['BTC-USD']):
        self.host = host
        self.port = port
        self.tickers = tickers

        self.orderbook = OBook(tickers=self.tickers)

    def begin(self):
        def start_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            serve = websockets.serve(self.the_server, self.host, self.port)
            loop.run_until_complete(serve)
            loop.run_forever()
        return threading.Thread(target=start_server)
            
    async def the_server(self, ws, path):
        while True:
            if self.orderbook.sync == True:
                data = self.orderbook.summation(depth=30)
                await ws.send(json.dumps(data))
                await asyncio.sleep(0.5)


TICKS = ['BTC-USD','ETH-USD','LTC-USD','ADA-USD','ETH-BTC','LTC-BTC','ADA-BTC', 'ZEC-USD']
server = Server(tickers=TICKS)

t1 = server.begin()
t2 = server.orderbook

t1.start()
t2.start()

t1.join()
t2.join()