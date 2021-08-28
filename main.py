import sqlite3
from app import apifunc as variable
from app import dbfunc as db
import time
import sys
import asyncio

printLines = True
lockBuy = False
db.ConnectToDatabase()

asyncio.run(variable.startOrderUpdateHandler())
variable.clientSocket.start()

async def asas():
    ts = variable.clientSocket.trade_socket('BNBBTC')
    # then start receiving messages
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)
asyncio.run(())

time.sleep(3000)
while True:
    ordersCountBuy = variable.updateOrdersCountBuy(printLines)

    ordersOnBuyBinance = variable.GetOpenOrdersBuy(printLines)
    ordersOnSellBinance = variable.GetOpenOrdersSell(printLines)
    summOrderCount = len(ordersOnBuyBinance) + len(ordersOnSellBinance)
    if(summOrderCount >= ordersCountBuy):
        lockBuy = True
    else:
        lockBuy = False
    
    #Если имеются открытые ордера на покупку:
    if(len(ordersOnBuyBinance) > 0 and lockBuy == False):
        for order in ordersOnBuyBinance:
            result = db.GetRowsBuyFromDatabase(order)
            #Если ордер не найден в БД:
            if (len(result) == 0):
                db.InsertInToDatabaseBuy(order = order, side='BUYBEFORE')
                print ("Информация об ордере сохранена в БД.")
            waitTime = int(str(order['time'])[:-3]) + variable.lifeTimeBuy * 60
            serverTime = variable.GetServerTime(printLines)
            
            if(serverTime > waitTime):
                print(f"Ордер создан более {variable.lifeTimeBuy} минут назад, меняем стоимость покупки.")
                variable.cancelOrder(order)

        if (len(ordersOnBuyBinance) >= ordersCountBuy) or (len(ordersOnSellBinance) >= ordersCountBuy):
            print(f"Открыто максимум ордеров на покупку: {len(ordersOnBuyBinance)} из {len(ordersOnBuyBinance)}")
        #Если количество открытых оредров меньше максимального - можем открыть еще:
        if (ordersCountBuy > len(ordersOnBuyBinance)) or (ordersCountBuy >= len(ordersOnSellBinance)):           
            #получаем последний открытый ордер и смотрем сколько минут прошло с открытия, если больше 1-2, то открываем еще один после анализа рынка
            lastOrderTime = db.GetLastBuyRowsFromDatabase()
            lastOrderTimeSecond = int(str(lastOrderTime[-1][0])[:-3]) + (2 * 60) 
            serverTime = variable.GetServerTime(printLines)
            delta = serverTime - lastOrderTimeSecond
            print(f"Прошло {delta}")
            print(str(lastOrderTime[-1][0])[:-3])
            if (lastOrderTimeSecond < serverTime ):
                prices = variable.GetPrices()
                minPrice = min(prices[-2:-1])
                variable.buyBUSD(minPrice)
            else:
                print(f"Можно открыть еще {ordersCountBuy - len(ordersOnBuyBinance)} ордер(ов). \n (Таймаут) Покупка через: {delta} секунд")
    
    if(len(ordersOnBuyBinance) == 0 and lockBuy == False):
        if(ordersCountBuy > len(ordersOnBuyBinance)):
            print(f"Можно открыть еще {ordersCountBuy - len(ordersOnBuyBinance)} ордер(ов)")
            prices = variable.GetPrices()
            minPrice = min(prices[-2:-1])
            variable.buyBUSD(minPrice)

    #Если имеются открытые ордера на продажу:
    if(len(ordersOnSellBinance) > 0):
        for order in ordersOnSellBinance:
            result = db.GetRowsSellFromDatabase(order)
            if (len(result) == 0):
                db.InsertInToDatabaseSell(order=order, side='SELLBEFORE')
            else:
                #Если ордер открыт больше двух часов назад и не продан - понижаем цену на 0.0001
                waitTime = int(str(order['time'])[:-3]) + variable.lifeTimeSell * 60
                serverTime = variable.GetServerTime(printLines)

                if(serverTime > waitTime):
                    variable.cancelOrder(order)
                    dempingPriceSell = float(order['price']) - 0.000100
                    dempingPriceSell = "{:0.0{}f}".format(dempingPriceSell, 6)
                    print(f"Ордер создан более двух часов назад, меняем стоимость продажи на {dempingPriceSell}.")
                    variable.buyBUSD(dempingPriceSell)
                else:
                    print(f"Ордер был создан менее {variable.lifeTimeSell} назад, ждем профит.")
    time.sleep(5)

