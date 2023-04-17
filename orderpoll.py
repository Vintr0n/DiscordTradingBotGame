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

def orderpoll():
mydb = mysql.connector.connect(host="SQLhostedserver.net",
                               user="username",
                               password="password",
                               database="databasename")
  mycursor = mydb.cursor()
  threading.Timer(10, orderpoll).start()  
  mycursor.execute("SELECT DISTINCT token FROM orders")
  results = mycursor.fetchall()
  for row in results:
      token = row[0]
      try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=" + token + "USDT",verify=False)
        data = response.json()
        #print(token + ' price: ' +data['price'])
      except:
          pass
      mycursor.execute("SELECT * FROM orders")
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
        currentprice = float(data['price'])
        #if long not executed yet
        if str(position) == "long" and str(executed) == "N" and currentprice <= orderprice:
          print('Order placed for: ' + str(ordertoken))
          #print(str(currentprice) + ' ' +str(orderprice))
          sql = "UPDATE orders SET Executed = %s WHERE id = %s"
          val = ('Y', int(orderID))
          mycursor.execute(sql,val)
          mydb.commit()
          sql = "INSERT INTO portfolio (UserID, Token, Amount, DateTime, Position) VALUES (%s, %s, %s, %s, %s)"
          now = datetime.now()
          #print(now)
          val = (str(userID), str(ordertoken), float(amount), now ,'long')
          mycursor.execute(sql,val)
          mydb.commit()
          deductable = amount * orderprice
          #print('Amount to be deducted from balance: ' + str(deductable))
          #SQL to take from balance next
          #then checks for tp and sl
          #close belongs in main.py
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            #print("Balance before: "+str(balance))
            newbalance = balance - deductable
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()
            newusers = mycursor.fetchall()
        #If short not executed yet
        elif str(position) == "short" and str(executed) == "N" and currentprice >= orderprice:
          print('Order placed for: ' + str(ordertoken))
          sql = "UPDATE orders SET Executed = %s WHERE id = %s"
          val = ('Y', int(orderID))
          mycursor.execute(sql,val)
          mydb.commit()
          sql = "INSERT INTO portfolio (UserID, Token, Amount, DateTime, Position) VALUES (%s, %s, %s, %s, %s)"
          now = datetime.now()
          #print(now)
          val = (str(userID), str(ordertoken), float(amount), now ,'short')
          mycursor.execute(sql,val)
          mydb.commit()
          deductable = amount * orderprice
          #print('Amount to be deducted from balance: ' + str(deductable))
          #SQL to take from balance next
          #then checks for tp and sl
          #close belongs in main.py
          mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
          users = mycursor.fetchall()
          for row in users:
            balance = row[2]
            #print("Balance before: "+str(balance))
            newbalance = balance - deductable
            sql = "UPDATE users SET Balance = %s WHERE ID = %s"
            val = (str(newbalance), str(userID))
            mycursor.execute(sql,val)
            mydb.commit()
            newusers = mycursor.fetchall()
orderpoll()