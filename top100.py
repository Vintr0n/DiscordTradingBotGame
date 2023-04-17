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

def top():
  threading.Timer(86400, top).start()
  #"https://s3.coinmarketcap.com/generated/core/crypto/cryptos.json"
  url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
  response = requests.get(url,verify=False)
  topresponse = response.json()
  tokens = []
  num = 100
  i = 0
  for _ in range(num):
    symbol = topresponse[i]['symbol']
    i = i +1
    if symbol not in tokens:
      tokens.append(symbol.upper())
  for x in tokens:
    time.sleep(0.0)
    try:
      response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=" + x + "USDT",verify=False)
      data = response.json()
      print(x + ' price: ' +data['price'])
      
    except:
        pass

top()


