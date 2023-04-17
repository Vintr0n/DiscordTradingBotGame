import discord
import os
import requests
import json
from discord.ext import commands
from replit import db
import mysql.connector
import urllib3
import urllib.request, json
from datetime import datetime
import threading
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def TPSLexecutor():
mydb = mysql.connector.connect(host="SQLhostedserver.net",
                               user="username",
                               password="password",
                               database="databasename")
    mycursor = mydb.cursor()
    threading.Timer(10, TPSLexecutor).start()
    mycursor.execute("SELECT * FROM orders WHERE Executed = 'Y'")
    orders = mycursor.fetchall()
    for row in orders:
        orderID = row[0]
        userID = row[1]
        position = row[2]
        ordertoken = row[3]
        amount = row[4]
        orderprice = float(row[5])
        tp = row[6]
        sl = row[7]
        date = row[8]
        executed = row[9]
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=" +
                ordertoken + "USDT",
                verify=False)
            data = response.json()
            currentprice = float(data['price'])
        except:
            pass
        if (currentprice >= tp and position == 'long'):
          print('Long TP hit for: ' + str(ordertoken))
          takeprofit = amount * tp
          mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken) + "'")
          mydb.commit()
          mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken)  + "'")
          mydb.commit()
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            newbalance = balance + takeprofit
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()
        elif (currentprice <= sl and position == 'long'):
          print('Long SL hit for: ' + str(ordertoken))
          stoploss = amount * sl
          mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken) + "'")
          mydb.commit()
          mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken) + "'")
          mydb.commit()
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            newbalance = balance + stoploss
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()
        #SHORT
        elif (currentprice <= tp and position == 'short'):
          tppercentagecalc = (orderprice-tp)/orderprice+1
          shorttakeprofit = orderprice * amount * tppercentagecalc
          #print(orderprice)
          #print(currentprice)
          #print(tp)
          #print(tppercentagecalc)
          #print(shorttakeprofit)
          print('Short TP hit for: ' + str(ordertoken))
          mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken) + "'")
          mydb.commit()
          mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken)  + "'")
          mydb.commit()
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            newbalance = balance + shorttakeprofit
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()
        elif (currentprice >= sl and position == 'short'):
          slpercentagecalc = 1+(orderprice-sl)/orderprice
          shortstoploss = orderprice * amount * slpercentagecalc
          #print(orderprice)
          #print(sl)
          #print(slpercentagecalc)
          #print(shortstoploss)
          print('Short SL hit for: ' + str(ordertoken))
          mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken) + "'")
          mydb.commit()
          mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                     " AND Token = '" + str(ordertoken)  + "'")
          mydb.commit()
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            newbalance = balance + shortstoploss
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()  
TPSLexecutor()
