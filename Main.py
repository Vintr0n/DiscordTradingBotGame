import discord
import os
import requests
import json
from discord.ext import commands
from replit import db
import mysql.connector
import urllib3
from datetime import datetime
import orderpoll
import TPSLexecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#############

mydb = mysql.connector.connect(host="SQLhostedserver.net",
                               user="username",
                               password="password",
                               database="databasename")
#Test connection:
mycursor = mydb.cursor()
#mycursor.execute("SELECT * FROM users")
#myresult = mycursor.fetchall()
#for x in myresult:
#    print(x)

########

bot = commands.Bot(command_prefix='!')

## API call to get top 100 into an array named top100
## If token string arguement isnt in the top100 then send message saying not top 100 token


### PRICE CHECK
@bot.command(name="price")
async def price(ctx, token: str):
    try:
      response = requests.get(
        "https://api.binance.com/api/v3/ticker/price?symbol=" + token + "USDT",
        verify=False)
      data = response.json()
      await ctx.channel.send("$" + token + " : " + data['price'])
    except:
        pass

#### SHOW BALANCE
@bot.command(name="balance")
async def register(ctx):
  mycursor.execute("SELECT * FROM users WHERE ID = " + str(ctx.message.author.id))
  myresult = mycursor.fetchall()
  for x in myresult:
      await ctx.channel.send("Your balance is: $" + str(x[2]))


#### REGISTER
@bot.command(name="register")
async def register(ctx):
    #await ctx.channel.send("Your ID is {}".format(ctx.message.author.name))
    #await ctx.channel.send("Your ID is {}".format(ctx.message.author.id))
    mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO users (ID, username, balance) VALUES (%s, %s, %s)"
    val = (str(ctx.message.author.id), ctx.message.author.name, 1000)
    mycursor.execute(sql, val)
    mydb.commit()
    
    row_count = mycursor.rowcount
    if row_count > 0:
        await ctx.channel.send("You have been registered!")
        print("MySQL Query execute:", mycursor.lastrowid)
        #await ctx.channel.send("User ID: " + str(ctx.message.author.id))
    elif row_count == 0:
        await ctx.channel.send("You are already registered!")
        #await ctx.channel.send("User ID: " + str(ctx.message.author.id))


###### EXECUTE LONG ORDER
#Amount = size / price (eg $100 of ETH worth 1500 = 0.66 ETH)
#Validation required: cant long and long again the same token and cant long and short same token, ALSO: if tp less than price or SL more than price etc
@bot.command(name="long")
async def price(ctx, token: str, size: float, price: float, tp: float,
                sl: float):
    #Select from orders the userid and the token - if there are rows then don't allow the order else continue to add the order (add to short and long)
    # row_count = mycursor.rowcount
    #if row_count == 0:
    #await ctx.channel.send("You do not have any assets in your portfolio!")
       
    await ctx.channel.send("Your order has been placed for: " + str(size) +
                           " worth of $" + token + "\n at a price of: " +
                           str(price) + "\n TP set to: " + str(tp) +
                           "\n SL set to: " + str(sl))
    sql = "INSERT INTO orders (userID, Position, Token, Amount, Price, TP, SL, DateTime, Executed) VALUES (%s, %s, %s, %s,%s, %s, %s,%s,%s)"
    now = datetime.now()
    amount = size / price
    val = (str(ctx.message.author.id), 'long', token, amount, price, tp, sl,
           now, 'N')
    mycursor.execute(sql, val)
    mydb.commit()
    print("MySQL Query execute:", mycursor.lastrowid)

@bot.command(name="short")
async def price(ctx, token: str, size: float, price: float, tp: float,
                sl: float):
    await ctx.channel.send("Your order has been placed for: " + str(size) +
                           " worth of $" + token + "\n at a price of: " +
                           str(price) + "\n TP set to: " + str(tp) +
                           "\n SL set to: " + str(sl))
    sql = "INSERT INTO orders (userID, Position, Token, Amount, Price, TP, SL, DateTime, Executed) VALUES (%s, %s, %s, %s,%s, %s, %s,%s,%s)"
    now = datetime.now()
    amount = size / price
    val = (str(ctx.message.author.id), 'short', token, amount, price, tp, sl,
           now, 'N')
    mycursor.execute(sql, val)
    mydb.commit()
    print("MySQL Query execute:", mycursor.lastrowid)
                  
###### SHOW ORDERS
@bot.command(name="orders")
async def orders(ctx):
    userID = str(ctx.message.author.id)
    mycursor.execute("SELECT * FROM orders WHERE UserID = " + userID +
                     " AND Executed <> 'Y'")
    orders = mycursor.fetchall()
    for x in orders:
        await ctx.channel.send(
            str(x[2]) + " | " + str(x[3]) + " | Amount: " + str(x[4]) +
            " | Price: " + str(x[5]) + " | TP: " + str(x[6]) + " | SL: " +
            str(x[7]))
    row_count = mycursor.rowcount
    if row_count == 0:
        await ctx.channel.send("You currently have no orders")


###### SHOW PORTFOLIO
@bot.command(name="portfolio")
async def portfolio(ctx):
    userID = str(ctx.message.author.id)
    mycursor.execute("SELECT * FROM portfolio WHERE UserID = " + userID)
    portfolio = mycursor.fetchall()
    for row in portfolio:
        userID = row[0]
        tokenowned = row[1]
        amountowned = row[2]
        datetimeorderexecuted = row[3]
        position = row[4]
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=" +
            tokenowned + "USDT",
            verify=False)
        data = response.json()
        currentprice = float(data['price'])
        currentvalue = amountowned * currentprice
        await ctx.channel.send("Position: " + str.title(position) + " | Token: " + str(tokenowned) + " | Amount: " + str(amountowned) + " | Current value: " + str(currentvalue))
    row_count = mycursor.rowcount
    if row_count == 0:
        await ctx.channel.send("You do not have any assets in your portfolio!")


###### CANCEL ORDER
@bot.command(name="cancel")
async def cancel(ctx, token: str):
    userID = str(ctx.message.author.id)
    mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                     " AND Token = '" + str(token) + "' AND Executed <> 'Y'")
    mydb.commit()
    row_count = mycursor.rowcount
    if row_count == 0:
        await ctx.channel.send("You do not have any open orders for " + token)
    elif row_count > 0:
        await ctx.channel.send("Your order for " + token +
                               " has been cancelled!")


###### CLOSE TRADE 
@bot.command(name="close")
async def close(ctx, token: str):
    userID = str(ctx.message.author.id)
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
        if str(token) == str(ordertoken):
            #Get current price for token
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=" + token +
                "USDT",
                verify=False)
            data = response.json()
            currentprice = float(data['price'])

            mycursor.execute("SELECT * FROM users WHERE ID = " + str(userID))
            users = mycursor.fetchall()
            for row in users:
                balance = row[2]
                if position == 'long':
                  #LONG: Update balance with new balance
                  currentvalue = float(amount) * float(currentprice)
                  newbalance = float(balance) + float(currentvalue)
                  sql = "UPDATE users SET Balance = %s WHERE ID = %s"
                  val = (str(newbalance), str(userID))
                  mycursor.execute(sql, val)
                  mydb.commit()
                  #Delete from orders
                  mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  #Delete from portfolio
                  mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  await ctx.channel.send("You have closed the trade for " +
                                   str(token) + " at a price of " +
                                   data['price'])

                elif (position == 'short' and currentprice == orderprice):
                  #SHORT: Update balance with new balance
                  currentvalue = float(amount) * float(currentprice)
                  newbalance = float(balance) + float(currentvalue)
                  sql = "UPDATE users SET Balance = %s WHERE ID = %s"
                  val = (str(newbalance), str(userID))
                  mycursor.execute(sql, val)
                  mydb.commit()

                  #Delete from orders
                  mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  #Delete from portfolio
                  mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  await ctx.channel.send("You have closed the trade for " +
                                   str(token) + " at a price of " +
                                   data['price'])

                elif (position == 'short' and currentprice < orderprice):
                  #SHORT: Update balance with new balance
                  shortinprofitcalc = (orderprice-currentprice)/orderprice+1
                  shortmakeprofit = orderprice * amount * shortinprofitcalc
                  #print(currentprice)
                  #print(shortinprofitcalc)
                  #print(shortmakeprofit)
                  #print("short in profit")
                  newbalance = float(balance) + float(shortmakeprofit)
                  sql = "UPDATE users SET Balance = %s WHERE ID = %s"
                  val = (str(newbalance), str(userID))
                  mycursor.execute(sql, val)
                  mydb.commit()

                  #Delete from orders
                  mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  #Delete from portfolio
                  mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  await ctx.channel.send("You have closed the trade for " +
                                   str(token) + " at a price of " +
                                   data['price'])


                elif (position == 'short' and currentprice > orderprice):
                  #SHORT: Update balance with new balance
                  shortinlosspercentagecalc = 1+(orderprice-currentprice)/orderprice
                  shortmakeloss = orderprice * amount * shortinlosspercentagecalc
                  #print(currentprice)
                  #print(shortinlosspercentagecalc)
                  #print(shortmakeloss)
                  #print("short in loss") 
                  newbalance = float(balance) + float(shortmakeloss)
                  sql = "UPDATE users SET Balance = %s WHERE ID = %s"
                  val = (str(newbalance), str(userID))
                  mycursor.execute(sql, val)
                  mydb.commit()
                  
                  #Delete from orders
                  mycursor.execute("DELETE FROM orders WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  #Delete from portfolio
                  mycursor.execute("DELETE FROM portfolio WHERE UserID = " + userID +
                             " AND Token = '" + str(token) + "'")
                  mydb.commit()

                  await ctx.channel.send("You have closed the trade for " +
                                   str(token) + " at a price of " +
                                   data['price'])

                  
#Instead of this do - if row is = 0 (results are zero) then post this message
        #elif str(token) != str(ordertoken):
            #await ctx.channel.send("You do not have an open trade for " +
                                   #str(token))


######
@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}')


my_secret = os.environ['testtest']

begin = 0

try:
    bot.run(my_secret)
except:
    os.system("kill 1")
