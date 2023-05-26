# echo-client.py

import asyncio
import json
from websockets.sync.client import connect
import itertools
import time

# python code om de register waardes door te sturen
dummy_values = [[1, 2], [3, 4]]
flat_dummies = list(itertools.chain(*dummy_values))
dict_ver = {k: v for k, v in enumerate(dummy_values[:3])}
HOST = "ws://192.168.4.1/ws"  #


def hello(k, v, websocket):
    websocket.send(bytes(json.dumps({k: v}), 'utf-8'))
    print({k: v})
    time.sleep(0.1)


with connect("ws://192.168.4.1/ws") as websocket:
    # bij connecteren worden word per lijst de waardes in json formaat doorgestuurd
    [hello(k, v, websocket) for k, v in enumerate(dummy_values)]
