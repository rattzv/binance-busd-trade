import configparser
import datetime
import os.path
import sqlite3
import time
import requests
import random
import app.dbfunc as db
import asyncio

from binance.websockets import BinanceSocketManager
from binance.client import Client
from binance.exceptions import BinanceAPIException

config = configparser.ConfigParser()
config.read('settings.ini')  

PUBLIC_KEY = config['API']['PUBLIC_KEY']
PRIVATE_KEY = config['API']['PRIVATE_KEY']
priceOneOrder = float(config['VARIABLES']['priceOneOrder'])
lifeTimeBuy = int(config['VARIABLES']['lifeTimeBuy'])
lifeTimeSell = int(config['VARIABLES']['lifeTimeSell'])

client = Client(api_key=PUBLIC_KEY, api_secret=PRIVATE_KEY)
clientSocket = BinanceSocketManager(client)

def orderUpdateHandler(msg):
    if(msg['e'] == 'executionReport'):
        if(msg['X'] == 'NEW'):
            if(msg['S'] == 'BUY'):
                db.InsertInToDatabaseBuy(order=msg, side='BUYHANDLER')
            if(msg['S'] == 'SELL'):
                db.InsertInToDatabaseSell(order=msg, side='SELLHANDLER')
        if(msg['X'] == 'CANCELED'):
            if(msg['S'] == 'BUY'):
                print(f"Отмена ордера на покупку по курсу: {msg['p']}, количество: {msg['q']}")
                #db.DelCanceledOrderFromDatabase(order=msg, side='BUY', isHandler=True)
            if(msg['S'] == 'SELL'):
                #db.DelCanceledOrderFromDatabase(order=msg, side='SELL', isHandler=True)
                print(f"Отмена ордера на продажу по курсу: {msg['p']}, количество: {msg['q']}")
        if(msg['X'] == 'FILLED'):
            if(msg['S'] == 'BUY'):
                priceSell = float(msg['p']) + 0.0001
                priceSell = "{:0.0{}f}".format(priceSell, 6)

                print(f"Ордер на покупку по курсу {msg['p']}$  исполнен, продаем по курсу {priceSell}$")
                sellBUSD(priceSell)




async def startOrderUpdateHandler():
    clientSocket.start_user_socket(orderUpdateHandler)


def updateOrdersCountBuy(printLines = False):
    priceOneOrder = float(config['VARIABLES']['priceOneOrder'])
    ordersCountBuy = int(config['VARIABLES']['ordersCountBuy'])

    balanceUSDT = client.get_asset_balance('USDT')
    freeBalanceUSDT = float(balanceUSDT['free'])
    ordersCountBuyMaximum = int(freeBalanceUSDT // priceOneOrder)
    print(ordersCountBuyMaximum)
    if(ordersCountBuyMaximum < ordersCountBuy):
        ordersCountBuy = ordersCountBuyMaximum
        if(printLines == True):
            print(f"Недосточно средст для заданного количества ордеров, максимальное значение изменено на доступное: {ordersCountBuy}")
    else:
        ordersCountBuy = int(config['VARIABLES']['ordersCountBuy'])
        if (printLines == True):
            print(f'Ручное ограничение максимального количества ордеров(manual): {ordersCountBuy}, доступно по текущему балансу: {ordersCountBuyMaximum}')
    return ordersCountBuy

def GetOpenOrdersBuy(printLines = False, symbol = 'BUSDUSDT'):
    openOrdersArray = client.get_open_orders(symbol=symbol)
    openOrderOnBuyCount = 0
    openOrderOnBuyArray = []

    for order in openOrdersArray:
        if order['side'] == 'BUY':
            openOrderOnBuyArray.append(order)
            openOrderOnBuyCount += 1
    if (printLines == True):
        print(f"Открытых заказов на покупку: {openOrderOnBuyCount} ")

        for orderOnBuy in openOrderOnBuyArray:
            print(f"   ID: {orderOnBuy['orderId']}, Дата: {orderOnBuy['time']}, цена: {orderOnBuy['price']},  Объем: {orderOnBuy['origQty']}, Тип: {orderOnBuy['type']}")
    return openOrderOnBuyArray

def GetOpenOrdersSell(printLines = False, symbol = 'BUSDUSDT'):
    openOrdersArray = client.get_open_orders(symbol=symbol)
    openOrderOnSellCount = 0
    openOrderOnSellArray = []

    for order in openOrdersArray:
        if order['side'] == 'SELL':
            openOrderOnSellArray.append(order)
            openOrderOnSellCount += 1
    if (printLines == True):
        print(f"Открытых заказов на продажу: {openOrderOnSellCount} ")

        for orderOnBuy in openOrderOnSellArray:
            print(f"   ID: {orderOnBuy['orderId']}, Дата: {orderOnBuy['time']}, цена: {orderOnBuy['price']},  Объем: {orderOnBuy['origQty']}, Тип: {orderOnBuy['type']}")
    return openOrderOnSellArray


def GetServerTime(printLines = False):
    currentServerTime = client.get_server_time()
    return int(str(currentServerTime['serverTime'])[:-3])

def GetPrices():
    candles = client.get_klines(symbol='BUSDUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)
    prices = []
    for a in candles:
        prices.append(float(a[4]))
    return prices

def buyBUSD(price, quantity = priceOneOrder, symbol = 'BUSDUSDT'):
    client.order_limit_buy(symbol=symbol, quantity = quantity, price = price, recvWindow=2000)

def sellBUSD(price, symbol = 'BUSDUSDT'):
    client.order_limit_sell(symbol=symbol, quantity = priceOneOrder, price = price, recvWindow=2000)
    
def cancelOrder(order, symbol = 'BUSDUSDT'):
    client.cancel_order(symbol = symbol, orderId = order['orderId'])
