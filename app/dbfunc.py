import sqlite3
import os
import time

def ConnectToDatabase():
    if os.path.isfile('orders_database.db'):
        print ("База данных сущестует, подключаемся...")
        db = sqlite3.connect('orders_database.db')
        db.close()
    else:
        print("Создание базы данных...")
        db = sqlite3.connect('orders_database.db')
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE ordersBuy
            (orderId text, clientOrderId text, symbol text, price text, quantity text, status text, side text, time text)''')
        db.commit()
        cursor.execute('''CREATE TABLE ordersSell
            (orderId text, clientOrderId text, symbol text, price text, quantity text, status text, side text, time text)''')
        db.commit()
        db.close()

def GetRowsBuyFromDatabase(order):
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM ordersBuy WHERE orderId = {order['orderId']}")
    return cursor.fetchall()

def GetRowsSellFromDatabase(order):
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM ordersSell WHERE orderId = {order['orderId']}")
    return cursor.fetchall()


def InsertInToDatabaseBuy(order, side):
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    if (side == 'BUYNOW'):
        orderBuild = (f'{order["orderId"]}', f'{order["clientOrderId"]}', f'{order["symbol"]}', f'{order["price"]}', f'{order["quantity"]}', f'{order["status"]}', f'{order["side"]}', f'{order["transactTime"]}')
        sql = ''' INSERT INTO ordersBuy(orderId, clientOrderId, symbol, quantity, price, status, side, time)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''
        cursor.execute(sql, orderBuild)
    if (side == 'BUYBEFORE'):
        orderBuild = (f'{order["orderId"]}', f'{order["clientOrderId"]}', f'{order["symbol"]}', f'{order["price"]}', f'{order["origQty"]}', f'{order["status"]}', f'{order["side"]}', f'{order["time"]}')
        sql = ''' INSERT INTO ordersBuy(orderId, clientOrderId, symbol, quantity, price, status, side, time)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''
    if (side == 'BUYHANDLER'):
        orderBuild = (f'{order["i"]}', f'{order["c"]}', f'{order["s"]}', f'{order["p"]}', f'{order["X"]}', f'{order["q"]}', f'{order["S"]}', f'{order["O"]}')
        sql = ''' INSERT INTO ordersBuy(orderId, clientOrderId, symbol, quantity, price,  status, side, time)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''
    cursor.execute(sql, orderBuild)
    db.commit()
    db.close()

def InsertInToDatabaseSell(order, side):
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    if (side == 'SELLNOW'):
        orderBuild = (f'{order["orderId"]}', f'{order["clientOrderId"]}', f'{order["symbol"]}', f'{order["price"]}', f'{order["quantity"]}', f'{order["status"]}', f'{order["side"]}', f'{order["transactTime"]}')
        sql = ''' INSERT INTO ordersSell(orderId, clientOrderId, symbol, price, quantity, status, side, time)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''
    if (side == 'SELLBEFORE'):
        orderBuild = (f'{order["orderId"]}', f'{order["clientOrderId"]}', f'{order["symbol"]}', f'{order["price"]}', f'{order["origQty"]}', f'{order["status"]}', f'{order["side"]}', f'{order["time"]}')
        sql = ''' INSERT INTO ordersSell(orderId, clientOrderId, symbol, price, quantity, status, side, time)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''
    if (side == 'SELLHANDLER'):
        orderBuild = (f'{order["i"]}', f'{order["c"]}', f'{order["s"]}', f'{order["p"]}', f'{order["X"]}', f'{order["q"]}', f'{order["S"]}', f'{order["O"]}')
        sql = ''' INSERT INTO ordersSell(orderId, clientOrderId, symbol, price, quantity, status, side, time)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?) '''

    cursor.execute(sql, orderBuild)
    db.commit()
    db.close()

def GetLastBuyRowsFromDatabase():
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    cursor.execute("SELECT time FROM ordersBuy WHERE status = 'NEW'")
    return cursor.fetchall()

def DelCanceledOrderFromDatabase(order, side, isHandler = False):
    db = sqlite3.connect('orders_database.db')
    cursor = db.cursor()
    if(isHandler == False):
        if (side == 'BUY'):
            cursor.execute(f'DELETE FROM ordersBuy WHERE orderId = {order["orderId"]}')
        if (side == 'SELL'):
            cursor.execute(f'DELETE FROM ordersSell WHERE orderId = {order["orderId"]}')
    else:
        if (side == 'BUY'):
            cursor.execute(f'DELETE FROM ordersBuy WHERE orderId = {order["i"]}')
        if (side == 'SELL'):
            cursor.execute(f'DELETE FROM ordersSell WHERE orderId = {order["i"]}')
    db.commit()
    db.close()